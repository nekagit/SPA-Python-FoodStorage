from sqlalchemy.orm import declarative_base
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import  Column, Float, Integer, String
Base = declarative_base()

class FoodModel(Base):
    __tablename__ = "food"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)       
    quantity = Column(Float, default=0.0)        
    minimal_stock = Column(Float, default=0.0)        
    unit = Column(String, default="units")       
    location = Column(String, default="pantry")  
    expiration_date = Column(String, nullable=True)


class Food(BaseModel):
    id: Optional[int] = None
    name: str
    category: str
    quantity: float
    minimal_stock: float
    unit: str
    location: str
    expiration_date: Optional[str] = None  

    model_config = ConfigDict(from_attributes=True)


class FoodUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    minimal_stock: Optional[float] = None
    unit: Optional[str] = None
    location: Optional[str] = None
    expiration_date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class FoodCategoryModel(Base):
    __tablename__ = "food_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


class FoodCategory(BaseModel):
    id: Optional[int] = None
    name: str
    model_config = ConfigDict(from_attributes=True)


class FoodCategoryUpdate(BaseModel):
    name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
