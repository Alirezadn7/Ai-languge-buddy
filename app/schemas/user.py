from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


from app.models.user import LanguageLevel


class UserProfileBase(BaseModel):
    native_language: str = Field(default="fa", max_length=50)
    target_language: str = Field(default="en", max_length=50)
    level: LanguageLevel = LanguageLevel.A1


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    native_language: str | None = Field(default=None, max_length=50)
    target_language: str | None = Field(default=None, max_length=50)
    level: LanguageLevel | None = None


class UserProfileOut(UserProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    
    password: str = Field(..., min_length=8, max_length=72)
    profile: UserProfileCreate = Field(default_factory=UserProfileCreate)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=72)
    is_active: bool | None = None


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    profile: UserProfileOut | None = None

    model_config = ConfigDict(from_attributes=True)
    

