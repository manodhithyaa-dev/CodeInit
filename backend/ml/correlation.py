"""
Correlation Analysis Module
Calculate Pearson correlation between mood and other factors
"""

import math
from typing import Optional
from sqlalchemy.orm import Session
from models.journal_model import JournalEntry
from models.fitness_log_model import FitnessLog
from models.medication_log_model import MedicationLog
from models.medication_model import Medication
from datetime import datetime, timedelta


def calculate_mean(values: list) -> float:
    """Calculate arithmetic mean"""
    if not values:
        return 0.0
    return sum(values) / len(values)


def calculate_pearson_correlation(x: list, y: list) -> float:
    """
    Calculate Pearson correlation coefficient
    Returns value between -1 and 1
    """
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    
    n = len(x)
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)
    
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    
    sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
    
    denominator = math.sqrt(sum_sq_x * sum_sq_y)
    
    if denominator == 0:
        return 0.0
    
    correlation = numerator / denominator
    return round(correlation, 3)


def get_mood_data(user_id: int, db: Session, days: int = 7) -> list:
    """Get daily mood scores for the past N days"""
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.created_at >= start_date
    ).order_by(JournalEntry.created_at).all()
    
    mood_by_date = {}
    for entry in entries:
        date_key = entry.created_at.date()
        if date_key not in mood_by_date:
            mood_by_date[date_key] = []
        if entry.sentiment_score:
            mood_by_date[date_key].append(float(entry.sentiment_score))
    
    # Average mood per day
    mood_data = []
    for date_key in sorted(mood_by_date.keys()):
        scores = mood_by_date[date_key]
        mood_data.append({
            "date": date_key,
            "avg_mood": calculate_mean(scores)
        })
    
    return mood_data


def get_fitness_data(user_id: int, db: Session, days: int = 7) -> list:
    """Get daily fitness data for the past N days"""
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    logs = db.query(FitnessLog).filter(
        FitnessLog.user_id == user_id,
        FitnessLog.log_date >= start_date
    ).order_by(FitnessLog.log_date).all()
    
    fitness_by_date = {}
    for log in logs:
        date_key = log.log_date
        if date_key not in fitness_by_date:
            fitness_by_date[date_key] = {"steps": 0, "minutes": 0, "completed": False}
        
        fitness_by_date[date_key]["steps"] += log.steps
        fitness_by_date[date_key]["minutes"] += log.minutes_exercised
        if log.activity_completed:
            fitness_by_date[date_key]["completed"] = True
    
    fitness_data = []
    for date_key in sorted(fitness_by_date.keys()):
        fd = fitness_by_date[date_key]
        # Create a composite fitness score
        score = (fd["steps"] / 1000) + (fd["minutes"] / 30) + (1 if fd["completed"] else 0)
        fitness_data.append({
            "date": date_key,
            "fitness_score": score
        })
    
    return fitness_data


def get_medication_adherence_data(user_id: int, db: Session, days: int = 7) -> list:
    """Get daily medication adherence for the past N days"""
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    medications = db.query(Medication).filter(
        Medication.user_id == user_id
    ).all()
    
    if not medications:
        return []
    
    med_ids = [m.id for m in medications]
    total_freq = sum(m.frequency_per_day for m in medications)
    
    logs = db.query(MedicationLog).filter(
        MedicationLog.medication_id.in_(med_ids),
        MedicationLog.taken_date >= start_date,
        MedicationLog.taken == True
    ).all()
    
    adherence_by_date = {}
    for log in logs:
        date_key = log.taken_date
        if date_key not in adherence_by_date:
            adherence_by_date[date_key] = 0
        adherence_by_date[date_key] += 1
    
    # Calculate adherence as percentage (0 to 1)
    adherence_data = []
    for i in range(days + 1):
        date_key = (datetime.utcnow().date() - timedelta(days=i))
        if date_key in adherence_by_date:
            adherence = min(1.0, adherence_by_date[date_key] / total_freq)
        else:
            adherence = 0.0
        adherence_data.append({
            "date": date_key,
            "adherence": adherence
        })
    
    return adherence_data


def calculate_mood_fitness_correlation(user_id: int, db: Session, days: int = 7) -> float:
    """
    Calculate correlation between mood and fitness activity
    Returns: Pearson correlation coefficient (-1 to 1)
    
    NOTE: Placeholder implementation. TODO: Replace with actual ML model
    """
    mood_data = get_mood_data(user_id, db, days)
    fitness_data = get_fitness_data(user_id, db, days)
    
    if not mood_data or not fitness_data:
        return 0.0
    
    # Align data by date
    mood_dict = {m["date"]: m["avg_mood"] for m in mood_data}
    fitness_dict = {f["date"]: f["fitness_score"] for f in fitness_data}
    
    common_dates = sorted(set(mood_dict.keys()) & set(fitness_dict.keys()))
    
    if len(common_dates) < 2:
        return 0.0
    
    moods = [mood_dict[d] for d in common_dates]
    fitness = [fitness_dict[d] for d in common_dates]
    
    return calculate_pearson_correlation(moods, fitness)


def calculate_mood_medication_correlation(user_id: int, db: Session, days: int = 7) -> float:
    """
    Calculate correlation between mood and medication adherence
    Returns: Pearson correlation coefficient (-1 to 1)
    
    NOTE: Placeholder implementation. TODO: Replace with actual ML model
    """
    mood_data = get_mood_data(user_id, db, days)
    medication_data = get_medication_adherence_data(user_id, db, days)
    
    if not mood_data or not medication_data:
        return 0.0
    
    # Align data by date
    mood_dict = {m["date"]: m["avg_mood"] for m in mood_data}
    med_dict = {m["date"]: m["adherence"] for m in medication_data}
    
    common_dates = sorted(set(mood_dict.keys()) & set(med_dict.keys()))
    
    if len(common_dates) < 2:
        return 0.0
    
    moods = [mood_dict[d] for d in common_dates]
    meds = [med_dict[d] for d in common_dates]
    
    return calculate_pearson_correlation(moods, meds)


def get_average_mood(user_id: int, db: Session, days: int = 7) -> float:
    """Calculate average mood score over past N days"""
    mood_data = get_mood_data(user_id, db, days)
    if not mood_data:
        return 0.0
    
    scores = [m["avg_mood"] for m in mood_data]
    return round(calculate_mean(scores), 3)
