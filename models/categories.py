from sqlmodel import Field, SQLModel
from typing import Optional
from .base import Base

class Category(Base, table=True):
    __tablename__ = "categories"
    
    name: str
    emoji: Optional[str] = Field(default=None)