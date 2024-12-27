"""Models of users/users requests"""
from datetime import date
from pydantic import BaseModel, Field, field_validator


class CreateUserRequest(BaseModel):
    """Register and login requset validation model"""
    username: str
    password: str


class EditUserRequest(BaseModel):
    """Edit requset validation model"""
    login: str | None = Field(None, description="Username")
    new_password: str | None = Field(None, description="Password")
    name: str | None = Field(None, description="Name")
    surname: str | None = Field(None, description="Surname")
    birth_date: date | None = Field(None, description="Birth date")
    sex: str | None = Field(None, description="Sex")
    email: str | None = Field(None, description="Email")

    @field_validator('birth_date')
    @classmethod
    def check_date(cls, d: date):
        """Validation of birth date. It can't be in the future"""
        if d > date.today():
            raise ValueError('Birth date cannot be in the future')
        return d
    

class ChangeUserSubscription(BaseModel):
    """Change user subscription plan"""
    user_id: int = Field(..., description="User id")
    set_to: bool = Field(..., description="Value of subscription plan")
