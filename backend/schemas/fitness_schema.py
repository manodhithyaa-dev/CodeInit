from pydantic import BaseModel
from datetime import date
from typing import Optional
import enum

class Intensity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class FitnessCreate(BaseModel):
    log_date: date
    activity_completed: bool = False
    steps: int = 0
    minutes_exercised: int = 0
    intensity: Intensity = Intensity.LOW

class FitnessResponse(BaseModel):
    id: int
    user_id: int
    log_date: date
    activity_completed: bool
    steps: int
    minutes_exercised: int
    intensity: Intensity

    class Config:
        from_attributes = True

class WeeklyFitnessResponse(BaseModel):
    total_steps: int
    total_minutes: int
    avg_intensity: str
    days_active: int
    current_streak: int
