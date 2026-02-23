from pydantic import BaseModel
from typing import Optional

class UserStatsResponse(BaseModel):
    journal: dict
    medications: dict
    fitness: dict
    user: dict
