from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# Profile Schemas
class ProfileBase(BaseModel):
    education: Optional[str] = None
    target_role: Optional[str] = "Software Engineer"
    experience_level: Optional[str] = "Fresher"
    skills: Optional[List[str]] = []

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Valid email address")
    full_name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    profile: Optional[ProfileResponse] = None
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
