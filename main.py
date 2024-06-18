from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import logging
 
# Configuration de la base de données
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://japhet:japhet@host.docker.internal:3306/items"
 
# Création de l'instance de moteur SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# Déclaration de la base pour la création de modèle
Base = declarative_base()
 
# Définition du modèle 
class Item(Base):
    __tablename__ = "items"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    description = Column(String(255), nullable=True)
    price = Column(Float)
    tax = Column(Float, nullable=True)
 
# Création des tables dans la base de données
try:
    Base.metadata.create_all(bind=engine)
except exc.SQLAlchemyError as e:
    logging.error(f"Error creating tables: {e}")
 
app = FastAPI()
 
# Définition des modèles Pydantic pour la validation des données
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
 
class ItemCreate(ItemBase):
    pass
 
class ItemInDB(ItemBase):
    id: int
 
class ItemOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
 
# Dépendance pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
# Routes CRUD pour gérer les items
@app.post("/items/", response_model=ItemOut)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    try:
        db.commit()
        db.refresh(db_item)
        return db_item
    except exc.SQLAlchemyError as e:
        logging.error(f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
 
@app.get("/items/", response_model=List[ItemOut])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        return db.query(Item).offset(skip).limit(limit).all()
    except exc.SQLAlchemyError as e:
        logging.error(f"Error reading items: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
 
@app.get("/items/{item_id}", response_model=ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item