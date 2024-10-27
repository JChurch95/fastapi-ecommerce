from sqlmodel import Field, SQLModel
from typing import Optional
from .base import Base

class Category(Base, table=True):
    __tablename__ = "categories"
    
    name: str
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    emoji: Optional[str] = Field(default=None)