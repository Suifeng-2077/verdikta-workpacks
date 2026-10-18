# flask2openapi

Build an OpenAPI 3.0.3 document from a Flask app, with the three things a caller actually needs: typed path
parameters read from the route itself, a **generated example for every schema** so the docs never show
`"string"`, and a **documented error envelope on every operation**.

## Install

```bash
pip install flask pydantic pyyaml openapi-spec-validator   # pyyaml only for YAML output
```

## Use

```python
from flask import Flask, jsonify
from pydantic import BaseModel, Field
from flask2openapi import describe

app = Flask(__name__)

class Item(BaseModel):
    id: int = Field(description="stable identifier")
    name: str
    price: float
    in_stock: bool = True

@app.get("/items/<int:item_id>")
@describe(response=Item, summary="Read one item", tags=["items"], errors=[404])
def get_item(item_id: int):
    return jsonify(Item(id=item_id, name="widget", price=9.5).model_dump())
```

```bash
python flask2openapi.py example_app:app -o openapi.yaml --title "Example API" --version 2.0.0
python flask2openapi.py example_app:app --format json
```

Only routes carrying `@describe` are documented. Anything else is left out rather than guessed at — a spec
that invents endpoints is worse than one with a gap.

## What the output gets right

- **Path parameters come from the Flask converters**, and the rule is rewritten to OpenAPI syntax:
  `/items/<int:item_id>` becomes `/items/{item_id}` with `{"type": "integer"}`. Leaving the Flask syntax in
  place is not cosmetic — the spec validator rejects it as an unresolvable parameter, which is exactly how
  this bug was found.
- **Every schema gets a generated example** from its own types: integers, floats, booleans, arrays, enums,
  and `email`/`date`/`date-time`/`uuid` formats. No `"string"` placeholders.
- **One shared error envelope** in `components.schemas.Error` with `code` and `message` required, referenced
  by every documented failure, plus a concrete example per status so the shape is obvious.
- **pydantic `$defs` are rewritten** to `#/components/schemas/...`, so no `$ref` in the document dangles.
- Deterministic output: routes are sorted, so regenerating produces a stable diff.

## Verified output

```
$ python flask2openapi.py example_app:app -o openapi.yaml --title "Example API" --version 2.0.0
wrote openapi.yaml: 2 paths, 2 operations

$ python -c "from openapi_spec_validator import validate; from openapi_spec_validator.readers import read_from_filename; s,_=read_from_filename('openapi.yaml'); validate(s); print('VALID', s['openapi'])"
VALID 3.0.3
```

`openapi-spec-validator` accepts the document with no errors. Paths: `/items` and `/items/{item_id}`;
schemas: `Item`, `NewItem`, `Error`.

A generated `404` response, in full:

```yaml
"404":
  description: Not Found — no resource with that identifier
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/Error'
      example:
        code: error_404
        message: no resource with that identifier
```

## Tests

```
$ python -m pytest -q
15 passed in 0.28s
```

In-process Flask app, no network. Covers: undocumented routes excluded, OpenAPI 3.0.3 shape, path parameter
typing from converters, pydantic model hoisted into components, no `#/$defs/` left anywhere, response example
generated from types, one shared error envelope with a concrete example, request body schema and example,
summary/tags/operationId carried through, YAML round-trip, enum and format examples, `$ref` resolution, a
clear rejection for non-pydantic models, Flask-rule-to-template conversion, and a regression test that every
declared path parameter appears in its own template.

## Limits, stated rather than discovered later

- Flask and pydantic v2 only. FastAPI already emits a document; this is for the app that has none.
- Query parameters are only documented when declared through a pydantic model on the route; there is no
  signature introspection yet.
- `errors=[...]` is explicit on purpose: guessing which failures an endpoint can produce is how specs end up
  describing 500s that cannot happen and omitting the 409 that can.
