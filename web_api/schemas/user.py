"""Models of users/users requests"""
from datetime import date
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from pydantic import BaseModel, Field, field_validator, model_validator
from repository.database import Base, engine
from fastapi import Form
from typing import Annotated, Optional

class CreateUserRequest(BaseModel):
    """Register and login requset validation model"""
    username: str
    password: str

class EditUserRequest(BaseModel):
    """Edit requset validation model"""
    username: str | None = Field(None, description="Username")
    new_password: str | None = Field(None, description="Password")
    birth_date: date | None = Field(None, description="Birth date")
    sex: str | None = Field(None, description="Sex")

    @field_validator('birth_date')
    @classmethod
    def check_date(cls, d: date):
        """Validation of birth date. It can't be in the future"""
        if d > date.today():
            raise ValueError('Birth date cannot be in the future')
        return d
