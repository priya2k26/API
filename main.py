from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ----------------- Database Setup -----------------
# Replace 'YOUR_MYSQL_PASSWORD' with the actual password for the 'priya' user
DATABASE_URL = "mysql+pymysql://priya:YOUR_MYSQL_PASSWORD@localhost/priya"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class DBItem(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    tax = Column(Float, nullable=True)

# ----------------- FastAPI App Setup -----------------
app = FastAPI(
    title="My API (MySQL Edition)",
    description="A basic FastAPI application with full CRUD support backed by MySQL",
    version="1.0.0"
)

# Pydantic Models for Input/Output
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None

class ItemResponse(ItemBase):
    id: int
    class Config:
        from_attributes = True

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------- Endpoints -----------------
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application! Connected to MySQL."}

@app.get("/items", response_model=dict)
def list_items(db: Session = Depends(get_db)):
    items = db.query(DBItem).all()
    # Convert SQLAlchemy models to Pydantic models for serialization
    items_dict = {item.id: ItemResponse.from_orm(item) for item in items}
    return {"items": items_dict}

@app.get("/items/{item_id}", response_model=dict)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": ItemResponse.from_orm(item)}

@app.post("/items", status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = DBItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": "Item created successfully", "item_id": db_item.id, "item": ItemResponse.from_orm(db_item)}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return {"message": "Item updated successfully", "item_id": item_id, "item": ItemResponse.from_orm(db_item)}

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully", "item_id": item_id}
