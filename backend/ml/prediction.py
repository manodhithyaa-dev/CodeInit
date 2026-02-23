"""
Mood Prediction Module
Predict next-day mood using Linear Regression
"""

from typing import Optional
from sqlalchemy.orm import Session
from models.journal_model import JournalEntry
from models.fitness_log_model import FitnessLog
from models.medication_log_model import MedicationLog
from models.medication_model import Medication
from datetime import datetime, timedelta
from .correlation import get_mood_data, calculate_mean


def predict_next_day_mood(user_id: int, db: Session, days: int = 14) -> float:
    """
    Predict next day's mood based on historical data
    
    Uses a simplified linear regression approach:
    - Features: previous day's mood, fitness level, medication adherence
    - Target: next day's mood
    
    Returns: Predicted mood score (-1 to 1)
    
    NOTE: This is a placeholder implementation.
    TODO: Replace with actual scikit-learn Linear Regression model
    """
    # Get historical data
    mood_data = get_mood_data(user_id, db, days)
    fitness_data = get_fitness_data_simple(user_id, db, days)
    med_data = get_medication_adherence_simple(user_id, db, days)
    
    if len(mood_data) < 3:
        # Not enough data, return neutral
        return 0.0
    
    # Build feature matrix and target
    # Features: [prev_mood, fitness_score, medication_adherence]
    # Target: current_mood
    
    mood_dict = {m["date"]: m["avg_mood"] for m in mood_data}
    fitness_dict = {f["date"]: f["score"] for f in fitness_data}
    med_dict = {m["date"]: m["adherence"] for m in med_data}
    
    all_dates = sorted(set(mood_dict.keys()) & set(fitness_dict.keys()) & set(med_dict.keys()))
    
    if len(all_dates) < 3:
        return calculate_mean([m["avg_mood"] for m in mood_data])
    
    # Simple moving average weighted prediction
    recent_moods = [mood_dict[d] for d in all_dates[-7:]]
    recent_fitness = [fitness_dict[d] for d in all_dates[-7:]]
    recent_meds = [med_dict[d] for d in all_dates[-7:]]
    
    avg_mood = calculate_mean(recent_moods)
    avg_fitness = calculate_mean(recent_fitness)
    avg_med = calculate_mean(recent_meds)
    
    # Weight factors (placeholder - ML model would learn these)
    weight_mood = 0.5
    weight_fitness = 0.3
    weight_med = 0.2
    
    # Calculate trend
    if len(recent_moods) >= 3:
        trend = (recent_moods[-1] - recent_moods[0]) / len(recent_moods)
    else:
        trend = 0.0
    
    # Base prediction
    prediction = (
        weight_mood * avg_mood +
        weight_fitness * (avg_fitness / 10) +  # Normalize fitness
        weight_med * avg_med
    )
    
    # Add trend adjustment
    prediction += trend * 0.3
    
    # Clamp to valid range
    prediction = max(-1.0, min(1.0, prediction))
    
    return round(prediction, 3)


def get_fitness_data_simple(user_id: int, db: Session, days: int = 7) -> list:
    """Get simplified fitness scores by date"""
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    logs = db.query(FitnessLog).filter(
        FitnessLog.user_id == user_id,
        FitnessLog.log_date >= start_date
    ).all()
    
    fitness_by_date = {}
    for log in logs:
        date_key = log.log_date
        if date_key not in fitness_by_date:
            fitness_by_date[date_key] = {"steps": 0, "minutes": 0}
        fitness_by_date[date_key]["steps"] += log.steps
        fitness_by_date[date_key]["minutes"] += log.minutes_exercised
    
    result = []
    for date_key, data in fitness_by_date.items():
        # Composite score
        score = (data["steps"] / 1000) + (data["minutes"] / 30)
        result.append({"date": date_key, "score": score})
    
    return result


def get_medication_adherence_simple(user_id: int, db: Session, days: int = 7) -> list:
    """Get simplified medication adherence by date"""
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    medications = db.query(Medication).filter(
        Medication.user_id == user_id
    ).all()
    
    if not medications:
        return [{"date": (datetime.utcnow().date() - timedelta(days=i)), "adherence": 0.0} for i in range(days)]
    
    med_ids = [m.id for m in medications]
    total_freq = sum(m.frequency_per_day for m in medications)
    
    logs = db.query(MedicationLog).filter(
        MedicationLog.medication_id.in_(med_ids),
        MedicationLog.taken_date >= start_date,
        MedicationLog.taken == True
    ).all()
    
    taken_by_date = {}
    for log in logs:
        if log.taken_date not in taken_by_date:
            taken_by_date[log.taken_date] = 0
        taken_by_date[log.taken_date] += 1
    
    result = []
    for i in range(days + 1):
        date_key = (datetime.utcnow().date() - timedelta(days=i))
        adherence = taken_by_date.get(date_key, 0) / total_freq if total_freq > 0 else 0.0
        result.append({"date": date_key, "adherence": adherence})
    
    return result


def generate_insight_summary(
    avg_mood: float,
    fitness_corr: float,
    medication_corr: float
) -> str:
    """
    Generate human-readable insight summary based on correlations
    
    Returns: Insight string
    """
    insights = []
    
    # Mood analysis
    if avg_mood >= 0.3:
        insights.append("You've been feeling positive lately.")
    elif avg_mood <= -0.3:
        insights.append("You've been feeling down recently.")
    else:
        insights.append("Your mood has been relatively neutral.")
    
    # Fitness correlation
    if fitness_corr > 0.3:
        insights.append("Exercise appears to boost your mood significantly.")
    elif fitness_corr > 0.1:
        insights.append("There's a slight connection between exercise and your mood.")
    elif fitness_corr < -0.3:
        insights.append("Your mood seems lower on more active days.")
    
    # Medication correlation
    if medication_corr > 0.3:
        insights.append("Medication adherence correlates with better mood.")
    elif medication_corr > 0.1:
        insights.append("Taking medication consistently may help your mood slightly.")
    
    return " ".join(insights)
