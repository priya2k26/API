from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="My API",
    description="A basic FastAPI application",
    version="1.0.0"
)

# Example data model
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application! The API is running."}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q, "status": "Success"}

@app.post("/item/{item_id}")
def create_item(item: Item):
    return {"message": "Item created successfully", "item": item}
