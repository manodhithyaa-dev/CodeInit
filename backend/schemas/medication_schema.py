from pydantic import BaseModel
from datetime import time, date
from typing import Optional, List

class MedicationCreate(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency_per_day: int = 1
    reminder_time: Optional[time] = None

class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency_per_day: Optional[int] = None
    reminder_time: Optional[time] = None

class MedicationResponse(BaseModel):
    id: int
    user_id: int
    name: str
    dosage: Optional[str] = None
    frequency_per_day: int
    reminder_time: Optional[time] = None

    class Config:
        from_attributes = True

class MedicationTakenRequest(BaseModel):
    taken_date: date
    taken: bool = True

class MedicationSummaryResponse(BaseModel):
    current_streak: int
    weekly_adherence: float
