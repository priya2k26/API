from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="My API",
    description="A basic FastAPI application with full CRUD support",
    version="1.0.0"
)

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None

items: dict[int, Item] = {}
next_item_id = 1

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application! The API is running."}

@app.get("/items")
def list_items():
    return {"items": items}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": items[item_id]}

@app.post("/items", status_code=201)
def create_item(item: Item):
    global next_item_id
    item_id = next_item_id
    next_item_id += 1
    items[item_id] = item
    return {"message": "Item created successfully", "item_id": item_id, "item": item}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")

    existing = items[item_id]
    updated_item = existing.copy(update=item.dict(exclude_unset=True))
    items[item_id] = updated_item
    return {"message": "Item updated successfully", "item_id": item_id, "item": updated_item}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {"message": "Item deleted successfully", "item_id": item_id}
