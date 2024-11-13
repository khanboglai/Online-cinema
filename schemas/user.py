"""Models of users/users requests"""
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from repository.database import Base
from fastapi import Form
from typing import Annotated

class User(Base):
    """Definition of table User"""
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)

class CreateUserRequest(BaseModel):
    """Register and login requset validation model"""
    username: str
    password: str
