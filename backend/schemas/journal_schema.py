from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional

class JournalCreate(BaseModel):
    content: str

class JournalUpdate(BaseModel):
    content: Optional[str] = None

class JournalResponse(BaseModel):
    id: int
    user_id: int
    content: str
    sentiment_score: Optional[float] = None
    emotion_label: Optional[str] = None
    risk_flag: bool
    created_at: datetime

    class Config:
        from_attributes = True

class JournalAnalysisResponse(BaseModel):
    sentiment_score: float
    emotion_label: str
    risk_flag: bool
