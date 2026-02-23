from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import enum

class PrimaryGoal(str, enum.Enum):
    MOOD = "MOOD"
    MEDICATION = "MEDICATION"
    FITNESS = "FITNESS"
    STRESS = "STRESS"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    age_range: str
    primary_goal: PrimaryGoal

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age_range: Optional[str] = None
    primary_goal: Optional[PrimaryGoal] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    age_range: Optional[str] = None
    primary_goal: PrimaryGoal
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    token: str
    user: UserResponse
