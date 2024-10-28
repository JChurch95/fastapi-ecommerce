from sqlmodel import Field, SQLModel
from typing import Optional
from .base import Base

class Brand(Base, table=True):
    __tablename__ = "brands"
    
    name: str