from sqlmodel import Field, SQLModel
from typing import Optional
from .base import Base

class SubCategory(Base, table=True):
    __tablename__ = "subcategories"
    
    name: str
    category_id: int = Field(foreign_key="categories.id")