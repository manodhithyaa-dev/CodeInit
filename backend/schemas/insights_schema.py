from pydantic import BaseModel

class WeeklyInsightsResponse(BaseModel):
    avg_mood: float
    fitness_correlation: float
    medication_correlation: float
    predicted_next_mood: float
    summary: str
