from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.journal_model import JournalEntry
from models.medication_model import Medication
from models.medication_log_model import MedicationLog
from models.fitness_log_model import FitnessLog
from datetime import date, timedelta
from typing import Optional

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Journal stats
    journal_count = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id
    ).count()
    
    journal_week = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.created_at >= week_ago
    ).count()
    
    # Medication stats
    medications = db.query(Medication).filter(
        Medication.user_id == current_user.id
    ).all()
    medication_count = len(medications)
    
    med_ids = [m.id for m in medications]
    med_taken_week = 0
    if med_ids:
        med_taken_week = db.query(MedicationLog).filter(
            MedicationLog.medication_id.in_(med_ids),
            MedicationLog.taken_date >= week_ago,
            MedicationLog.taken == True
        ).count()
    
    # Fitness stats
    fitness_logs = db.query(FitnessLog).filter(
        FitnessLog.user_id == current_user.id
    ).count()
    
    fitness_week = db.query(FitnessLog).filter(
        FitnessLog.user_id == current_user.id,
        FitnessLog.log_date >= week_ago,
        FitnessLog.activity_completed == True
    ).count()
    
    total_steps_week = 0
    logs_week = db.query(FitnessLog).filter(
        FitnessLog.user_id == current_user.id,
        FitnessLog.log_date >= week_ago
    ).all()
    if logs_week:
        total_steps_week = sum(log.steps for log in logs_week)
    
    # Calculate streaks
    # Medication streak
    med_streak = 0
    if medications and med_ids:
        total_freq = sum(m.frequency_per_day for m in medications)
        check_date = today
        while True:
            day_logs = db.query(MedicationLog).filter(
                MedicationLog.medication_id.in_(med_ids),
                MedicationLog.taken_date == check_date,
                MedicationLog.taken == True
            ).count()
            if day_logs >= total_freq:
                med_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
    
    # Fitness streak
    fit_streak = 0
    check_date = today
    while True:
        day_log = db.query(FitnessLog).filter(
            FitnessLog.user_id == current_user.id,
            FitnessLog.log_date == check_date,
            FitnessLog.activity_completed == True
        ).first()
        if day_log:
            fit_streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    return {
        "journal": {
            "total_entries": journal_count,
            "entries_this_week": journal_week
        },
        "medications": {
            "total_medications": medication_count,
            "doses_taken_this_week": med_taken_week,
            "current_streak": med_streak
        },
        "fitness": {
            "total_logs": fitness_logs,
            "days_active_this_week": fitness_week,
            "total_steps_this_week": total_steps_week,
            "current_streak": fit_streak
        },
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "primary_goal": current_user.primary_goal.value
        }
    }
