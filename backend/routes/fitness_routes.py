from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.fitness_log_model import FitnessLog, Intensity
from schemas.fitness_schema import (
    FitnessCreate, FitnessResponse, 
    WeeklyFitnessResponse, Intensity as IntensityEnum
)
from typing import List
from datetime import date, timedelta

router = APIRouter(prefix="/fitness", tags=["Fitness"])

@router.post("", response_model=FitnessResponse)
def create_fitness_log(
    fitness: FitnessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(FitnessLog).filter(
        FitnessLog.user_id == current_user.id,
        FitnessLog.log_date == fitness.log_date
    ).first()
    
    if existing:
        existing.activity_completed = fitness.activity_completed
        existing.steps = fitness.steps
        existing.minutes_exercised = fitness.minutes_exercised
        existing.intensity = Intensity[fitness.intensity.value]
        db.commit()
        db.refresh(existing)
        return existing
    
    db_fitness = FitnessLog(
        user_id=current_user.id,
        log_date=fitness.log_date,
        activity_completed=fitness.activity_completed,
        steps=fitness.steps,
        minutes_exercised=fitness.minutes_exercised,
        intensity=Intensity[fitness.intensity.value]
    )
    db.add(db_fitness)
    db.commit()
    db.refresh(db_fitness)
    return db_fitness

@router.get("", response_model=List[FitnessResponse])
def get_fitness_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(FitnessLog).filter(
        FitnessLog.user_id == current_user.id
    ).order_by(FitnessLog.log_date.desc()).all()

@router.get("/weekly", response_model=WeeklyFitnessResponse)
def get_weekly_fitness(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    week_ago = today - timedelta(days=6)
    
    logs = db.query(FitnessLog).filter(
        FitnessLog.user_id == current_user.id,
        FitnessLog.log_date >= week_ago,
        FitnessLog.log_date <= today
    ).all()
    
    if not logs:
        return WeeklyFitnessResponse(
            total_steps=0, total_minutes=0, 
            avg_intensity="LOW", days_active=0, current_streak=0
        )
    
    total_steps = sum(log.steps for log in logs)
    total_minutes = sum(log.minutes_exercised for log in logs)
    days_active = sum(1 for log in logs if log.activity_completed)
    
    intensity_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    avg_intensity_val = sum(intensity_map.get(log.intensity.value, 1) for log in logs) / len(logs)
    avg_intensity = "LOW" if avg_intensity_val < 1.5 else "MEDIUM" if avg_intensity_val < 2.5 else "HIGH"
    
    streak = 0
    check_date = today
    while True:
        day_log = db.query(FitnessLog).filter(
            FitnessLog.user_id == current_user.id,
            FitnessLog.log_date == check_date,
            FitnessLog.activity_completed == True
        ).first()
        
        if day_log:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    return WeeklyFitnessResponse(
        total_steps=total_steps,
        total_minutes=total_minutes,
        avg_intensity=avg_intensity,
        days_active=days_active,
        current_streak=streak
    )
