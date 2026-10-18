"""A tiny Flask app used to demonstrate and test flask2openapi."""

from __future__ import annotations

from flask import Flask, jsonify
from pydantic import BaseModel, Field

from flask2openapi import describe

app = Flask(__name__)


class Item(BaseModel):
    id: int = Field(description="stable identifier")
    name: str
    price: float
    in_stock: bool = True
    tags: list[str] = []


class NewItem(BaseModel):
    name: str
    price: float


@app.get("/items/<int:item_id>")
@describe(response=Item, summary="Read one item", tags=["items"], errors=[404])
def get_item(item_id: int):
    return jsonify(Item(id=item_id, name="widget", price=9.5).model_dump())


@app.post("/items")
@describe(request=NewItem, response=Item, summary="Create an item", tags=["items"], errors=[400, 422])
def create_item():
    return jsonify(Item(id=1, name="widget", price=9.5).model_dump()), 201


@app.get("/health")
def health():
    """Deliberately undescribed: it must not appear in the generated document."""
    return {"ok": True}
