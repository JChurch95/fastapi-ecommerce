from sqlmodel import Field, SQLModel
from typing import Optional
from .base import Base

class Product(Base, table=True):
    __tablename__ = "products"
    
    name: str
    brand: str
    price: int
    description: str
    subcategory_id: int = Field(foreign_key="subcategories.id")
    image_url: Optional[str] = None
    rating_value: int = Field(default=39)
    rating_count: int = Field(default=120)