from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class LanguageLevel(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class UserProfileBase(BaseModel):
    native_language: str = Field(default="fa", max_length=50)
    target_language: str = Field(default="en", max_length=50)
    level: LanguageLevel = LanguageLevel.A1


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    native_language: Optional[str] = Field(None, max_length=50)
    target_language: Optional[str] = Field(None, max_length=50)
    level: Optional[LanguageLevel] = None


class UserProfileOut(UserProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    profile: Optional[UserProfileCreate] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    is_active: Optional[bool] = None


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    profile: Optional[UserProfileOut] = None

    model_config = ConfigDict(from_attributes=True)

    

