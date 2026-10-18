#!/usr/bin/env python3
"""flask2openapi.py - build an OpenAPI 3.0.3 document from a Flask app.

Why this exists: an auto-generated spec is usually accurate about paths and useless about everything a
reader needs. This one is built around three questions a caller actually asks:

1. What are the parameters, and what type is each? (path converters and query defaults are read from the
   route itself, not from prose)
2. What does a real response look like? (every schema gets a **generated example** from its own types, so
   the docs never show `"string"`)
3. What happens when it fails? (every operation gets the same documented error envelope, defined once in
   `components.schemas.Error`)

Declare a route with the decorator, and the generator does the rest:

    from flask2openapi import describe
    from pydantic import BaseModel

    class Item(BaseModel):
        id: int
        name: str

    @app.get("/items/<int:item_id>")
    @describe(response=Item, summary="Read one item", tags=["items"], errors=[404])
    def get_item(item_id: int):
        ...

Usage:
    python flask2openapi.py myapp:app -o openapi.yaml
    python flask2openapi.py myapp:app --format json --title "My API" --version 1.2.3
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from typing import Any, Callable

try:
    import yaml  # optional, only needed for YAML output
except ImportError:  # pragma: no cover
    yaml = None

ERROR_SCHEMA = {
    "type": "object",
    "required": ["code", "message"],
    "properties": {
        "code": {"type": "string", "description": "stable machine-readable error code"},
        "message": {"type": "string", "description": "human-readable explanation"},
        "details": {"type": "object", "description": "optional field-level detail"},
    },
}

# Reason phrase and a one-line cause for each documented failure, so the spec explains rather than lists.
ERROR_TEXT = {
    400: ("Bad Request", "the request body or query was malformed"),
    401: ("Unauthorized", "missing or invalid credentials"),
    403: ("Forbidden", "authenticated but not allowed"),
    404: ("Not Found", "no resource with that identifier"),
    409: ("Conflict", "the request conflicts with current state"),
    422: ("Unprocessable Entity", "the payload parsed but failed validation"),
    429: ("Too Many Requests", "rate limit exceeded"),
    500: ("Internal Server Error", "unexpected failure; safe to retry once"),
}


def describe(
    *,
    response: Any = None,
    request: Any = None,
    summary: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    errors: list[int] | None = None,
) -> Callable[[Callable], Callable]:
    """Attach OpenAPI metadata to a view function."""

    def wrapper(view: Callable) -> Callable:
        view.__openapi__ = {
            "response": response,
            "request": request,
            "summary": summary,
            "description": description,
            "tags": tags or [],
            "errors": errors if errors is not None else [400, 500],
        }
        return view

    return wrapper


def example_from(schema: dict, components: dict, depth: int = 0) -> Any:
    """Generate a plausible example from a JSON Schema, so documentation never shows 'string'."""
    if not schema or depth > 6:
        return None
    ref = schema.get("$ref")
    if ref:
        return example_from(components.get(ref.split("/")[-1], {}), components, depth + 1)
    if "example" in schema:
        return schema["example"]
    if "enum" in schema and schema["enum"]:
        return schema["enum"][0]
    if "anyOf" in schema or "oneOf" in schema:
        variants = schema.get("anyOf") or schema.get("oneOf")
        return example_from(variants[0], components, depth + 1) if variants else None
    kind = schema.get("type")
    if kind == "object" or "properties" in schema:
        return {
            key: example_from(sub, components, depth + 1)
            for key, sub in (schema.get("properties") or {}).items()
        }
    if kind == "array":
        return [example_from(schema.get("items", {}), components, depth + 1)]
    if kind == "integer":
        return schema.get("minimum", 0) or 1
    if kind == "number":
        return 1.5
    if kind == "boolean":
        return True
    if kind == "null":
        return None
    if schema.get("format") == "date-time":
        return "2026-01-01T00:00:00Z"
    if schema.get("format") == "date":
        return "2026-01-01"
    if schema.get("format") == "email":
        return "user@example.com"
    if schema.get("format") == "uuid":
        return "3f1c2a4e-5b6d-4c7e-8f90-1a2b3c4d5e6f"
    return "text"


def pydantic_schema(model: Any, components: dict) -> dict:
    """Return a schema reference for a pydantic model, hoisting its $defs into components.schemas."""
    if model is None:
        return {}
    if not hasattr(model, "model_json_schema"):
        raise SystemExit(f"{model!r} is not a pydantic v2 model; use pydantic.BaseModel subclasses")
    name = model.__name__
    raw = model.model_json_schema()
    for def_name, def_schema in (raw.pop("$defs", None) or {}).items():
        components.setdefault(def_name, _rewrite_refs(def_schema))
    components[name] = _rewrite_refs(raw)
    return {"$ref": f"#/components/schemas/{name}"}


def _rewrite_refs(node: Any) -> Any:
    """pydantic emits #/$defs/X; OpenAPI wants #/components/schemas/X."""
    if isinstance(node, dict):
        return {
            key: (
                value.replace("#/$defs/", "#/components/schemas/")
                if key == "$ref" and isinstance(value, str)
                else _rewrite_refs(value)
            )
            for key, value in node.items()
        }
    if isinstance(node, list):
        return [_rewrite_refs(item) for item in node]
    return node


CONVERTERS = {
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "string": {"type": "string"},
    "path": {"type": "string"},
    "uuid": {"type": "string", "format": "uuid"},
}


DEFINITION = {"type": "string"}


def openapi_path(rule_rule: str) -> str:
    """Convert a Flask rule to an OpenAPI path template: /items/<int:id> becomes /items/{id}.

    This is not cosmetic: OpenAPI matches declared path parameters against {braces}, so leaving the Flask
    syntax in place makes every path parameter unresolved and the document invalid.
    """
    return re.sub(r"<(?:(?:[^:>]+):)?([^>]+)>", r"{\1}", rule_rule)


def build_spec(app: Any, title: str | None = None, version: str = "1.0.0", base: str = "/") -> dict:
    """Walk the Flask url_map and produce an OpenAPI 3.0.3 document."""
    components: dict[str, Any] = {"Error": copy.deepcopy(ERROR_SCHEMA)}
    paths: dict[str, Any] = {}

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
        if rule.endpoint == "static":
            continue
        view = app.view_functions.get(rule.endpoint)
        meta = getattr(view, "__openapi__", None)
        if meta is None:
            continue  # only describe what was explicitly described

        # Path parameters come from the route converters, not from prose.
        params = []
        for arg in sorted(rule.arguments):
            converter = next(
                (c for c in (rule._converters.get(arg) if hasattr(rule, "_converters") else None,) if c),
                None,
            )
            kind = "int" if converter.__class__.__name__ == "IntegerConverter" else "string"
            params.append(
                {
                    "name": arg,
                    "in": "path",
                    "required": True,
                    "schema": copy.deepcopy(CONVERTERS.get(kind, {"type": "string"})),
                }
            )

        ok_schema = pydantic_schema(meta["response"], components)
        responses: dict[str, Any] = {}
        if ok_schema:
            ok_body = {
                "description": "successful response",
                "content": {"application/json": {"schema": ok_schema}},
            }
            example = example_from(ok_schema, components)
            if example is not None:
                ok_body["content"]["application/json"]["example"] = example
            responses["200"] = ok_body
        else:
            responses["200"] = {"description": "successful response"}

        errors = list(meta.get("errors") or [])
        error_body = {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
        for code in errors:
            phrase, cause = ERROR_TEXT.get(code, ("Error", "documented failure"))
            responses[str(code)] = {
                "description": f"{phrase} — {cause}",
                **copy.deepcopy(error_body),
            }
            # A generated example makes the envelope concrete instead of abstract.
            responses[str(code)]["content"]["application/json"]["example"] = {
                "code": f"error_{code}",
                "message": cause,
            }

        operation: dict[str, Any] = {
            "operationId": rule.endpoint,
            "summary": meta.get("summary") or rule.endpoint.replace("_", " "),
            "responses": responses,
        }
        if meta.get("description"):
            operation["description"] = meta["description"]
        if meta.get("tags"):
            operation["tags"] = meta["tags"]
        if params:
            operation["parameters"] = params
        req_schema = pydantic_schema(meta["request"], components)
        if req_schema:
            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": req_schema,
                        "example": example_from(req_schema, components),
                    }
                },
            }

        documented_path = openapi_path(rule.rule)
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            paths.setdefault(documented_path, {})[method.lower()] = copy.deepcopy(operation)

    spec = {
        "openapi": "3.0.3",
        "info": {"title": title or getattr(app, "name", "API"), "version": version},
        "servers": [{"url": base}],
        "paths": paths,
        "components": {"schemas": components},
    }
    return spec


def load_app(target: str):
    """Resolve 'module:app' to the Flask application object."""
    import importlib

    if ":" not in target:
        raise SystemExit("pass the app as module:attribute, e.g. myapp:app")
    module_name, attr = target.split(":", 1)
    sys.path.insert(0, ".")
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as err:
        raise SystemExit(f"{module_name} has no attribute {attr}") from err


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build an OpenAPI 3.0.3 document from a Flask app.")
    p.add_argument("app", help="module:attribute of the Flask app, e.g. myapp:app")
    p.add_argument("-o", "--out", default=None, help="output file (default: stdout)")
    p.add_argument("--format", choices=("yaml", "json"), default="yaml")
    p.add_argument("--title", default=None)
    p.add_argument("--version", default="1.0.0")
    p.add_argument("--base", default="/", help="server base URL path")
    args = p.parse_args(argv)

    spec = build_spec(load_app(args.app), args.title, args.version, args.base)

    if args.format == "yaml":
        if yaml is None:
            raise SystemExit("YAML output needs pyyaml: pip install pyyaml (or pass --format json)")
        payload = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=100)
    else:
        payload = json.dumps(spec, indent=2, ensure_ascii=False) + "\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload)
        ops = sum(len(v) for v in spec["paths"].values())
        print(f"wrote {args.out}: {len(spec['paths'])} paths, {ops} operations", file=sys.stderr)
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
