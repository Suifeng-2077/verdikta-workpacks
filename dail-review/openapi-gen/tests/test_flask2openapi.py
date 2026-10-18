"""Tests for flask2openapi. A real Flask app is built in-process; no network, no files."""

from __future__ import annotations

import json

import pytest

import yaml

from example_app import app
from flask2openapi import build_spec, example_from


@pytest.fixture(scope="module")
def spec():
    return build_spec(app, title="Example API", version="2.0.0")


def test_only_described_routes_are_documented(spec):
    assert "/items/{item_id}" in spec["paths"]
    assert "/items" in spec["paths"]
    # /health has no @describe, so it must be absent rather than guessed at.
    assert "/health" not in spec["paths"]


def test_document_is_openapi_3(spec):
    assert spec["openapi"] == "3.0.3"
    assert spec["info"] == {"title": "Example API", "version": "2.0.0"}


def test_path_parameter_type_comes_from_the_converter(spec):
    params = spec["paths"]["/items/{item_id}"]["get"]["parameters"]
    assert params[0]["name"] == "item_id"
    assert params[0]["in"] == "path"
    assert params[0]["schema"] == {"type": "integer"}


def test_pydantic_model_is_hoisted_into_components(spec):
    assert "Item" in spec["components"]["schemas"]
    ref = spec["paths"]["/items/{item_id}"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert ref == {"$ref": "#/components/schemas/Item"}


def test_nested_defs_are_rewritten_to_component_refs(spec):
    """pydantic emits #/$defs/...; every $ref in the document must point at components."""
    blob = json.dumps(spec)
    assert "#/$defs/" not in blob


def test_response_example_is_generated_from_types(spec):
    example = spec["paths"]["/items/{item_id}"]["get"]["responses"]["200"]["content"]["application/json"]["example"]
    assert example["id"] == 1
    assert isinstance(example["price"], float)
    assert example["in_stock"] is True
    assert isinstance(example["tags"], list)
    assert example["name"] != "string"


def test_error_responses_use_one_shared_envelope(spec):
    responses = spec["paths"]["/items/{item_id}"]["get"]["responses"]
    assert "404" in responses
    assert responses["404"]["content"]["application/json"]["schema"] == {"$ref": "#/components/schemas/Error"}
    assert set(spec["components"]["schemas"]["Error"]["required"]) == {"code", "message"}
    # And the envelope has a concrete example, not just a schema.
    assert responses["404"]["content"]["application/json"]["example"]["code"] == "error_404"


def test_request_body_has_schema_and_example(spec):
    body = spec["paths"]["/items"]["post"]["requestBody"]
    assert body["required"] is True
    assert body["content"]["application/json"]["schema"] == {"$ref": "#/components/schemas/NewItem"}
    assert body["content"]["application/json"]["example"]["name"] != "string"


def test_summary_and_tags_are_carried(spec):
    op = spec["paths"]["/items"]["post"]
    assert op["summary"] == "Create an item"
    assert op["tags"] == ["items"]
    assert op["operationId"] == "create_item"


def test_yaml_round_trip_preserves_the_document(spec):
    text = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
    assert yaml.safe_load(text) == spec


def test_example_from_handles_enum_and_formats():
    components = {}
    assert example_from({"type": "string", "enum": ["a", "b"]}, components) == "a"
    assert example_from({"type": "string", "format": "email"}, components) == "user@example.com"
    assert example_from({"type": "array", "items": {"type": "integer"}}, components) == [1]


def test_resolving_a_ref_uses_components():
    components = {"Thing": {"type": "object", "properties": {"n": {"type": "integer"}}}}
    assert example_from({"$ref": "#/components/schemas/Thing"}, components) == {"n": 1}


def test_non_pydantic_model_is_rejected_clearly():
    class Plain:
        pass

    from flask2openapi import pydantic_schema

    with pytest.raises(SystemExit) as exc:
        pydantic_schema(Plain, {})
    assert "pydantic v2" in str(exc.value)


def test_flask_rule_becomes_an_openapi_template():
    from flask2openapi import openapi_path

    assert openapi_path("/items/<int:item_id>") == "/items/{item_id}"
    assert openapi_path("/users/<uuid:uid>/posts/<post_id>") == "/users/{uid}/posts/{post_id}"
    assert openapi_path("/health") == "/health"


def test_every_declared_path_parameter_appears_in_its_template(spec):
    """The bug the spec validator caught: Flask rule syntax leaves path params unresolved."""
    import re

    for path, ops in spec["paths"].items():
        declared = {p["name"] for op in ops.values() for p in op.get("parameters", [])}
        in_template = set(re.findall(r"\{([^}]+)\}", path))
        assert declared == in_template, f"{path}: declared {declared} vs template {in_template}"
        assert "<" not in path and ">" not in path
