from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CircleCreate(BaseModel):
    name: str

class CircleUpdate(BaseModel):
    name: Optional[str] = None

class CircleResponse(BaseModel):
    id: int
    name: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class CircleMemberResponse(BaseModel):
    id: int
    user_id: int
    role: str

    class Config:
        from_attributes = True

class CircleWithMembers(BaseModel):
    id: int
    name: str
    created_by: int
    members: List[CircleMemberResponse]

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    receiver_id: int
    message: str

class MessageResponse(BaseModel):
    id: int
    circle_id: int
    sender_id: int
    receiver_id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
