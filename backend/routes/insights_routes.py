from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from schemas.insights_schema import WeeklyInsightsResponse
from ml.correlation import (
    calculate_mood_fitness_correlation,
    calculate_mood_medication_correlation,
    get_average_mood
)
from ml.prediction import predict_next_day_mood, generate_insight_summary

router = APIRouter(prefix="/insights", tags=["Insights"])

@router.get("/weekly", response_model=WeeklyInsightsResponse)
def get_weekly_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Calculate metrics using ML modules
    avg_mood = get_average_mood(current_user.id, db, days=7)
    fitness_correlation = calculate_mood_fitness_correlation(current_user.id, db, days=7)
    medication_correlation = calculate_mood_medication_correlation(current_user.id, db, days=7)
    predicted_mood = predict_next_day_mood(current_user.id, db, days=14)
    
    # Generate human-readable summary
    summary = generate_insight_summary(avg_mood, fitness_correlation, medication_correlation)
    
    return WeeklyInsightsResponse(
        avg_mood=avg_mood,
        fitness_correlation=fitness_correlation,
        medication_correlation=medication_correlation,
        predicted_next_mood=predicted_mood,
        summary=summary
    )
