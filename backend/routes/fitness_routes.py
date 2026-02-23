from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.fitness_log_model import FitnessLog, Intensity
from schemas.fitness_schema import (
    FitnessCreate, FitnessResponse, 
    WeeklyFitnessResponse, Intensity as IntensityEnum,
    FitnessUpdate, MonthlyFitnessResponse
)
from typing import List, Optional
from datetime import date, timedelta
from calendar import monthrange

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
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FitnessLog).filter(FitnessLog.user_id == current_user.id)
    
    if start_date:
        query = query.filter(FitnessLog.log_date >= start_date)
    if end_date:
        query = query.filter(FitnessLog.log_date <= end_date)
    
    offset = (page - 1) * limit
    logs = query.order_by(FitnessLog.log_date.desc()).offset(offset).limit(limit).all()
    return logs

@router.get("/{log_id}", response_model=FitnessResponse)
def get_fitness_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = db.query(FitnessLog).filter(
        FitnessLog.id == log_id,
        FitnessLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Fitness log not found")
    
    return log

@router.put("/{log_id}", response_model=FitnessResponse)
def update_fitness_log(
    log_id: int,
    fitness: FitnessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = db.query(FitnessLog).filter(
        FitnessLog.id == log_id,
        FitnessLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Fitness log not found")
    
    if fitness.log_date is not None:
        log.log_date = fitness.log_date
    if fitness.activity_completed is not None:
        log.activity_completed = fitness.activity_completed
    if fitness.steps is not None:
        log.steps = fitness.steps
    if fitness.minutes_exercised is not None:
        log.minutes_exercised = fitness.minutes_exercised
    if fitness.intensity is not None:
        log.intensity = Intensity[fitness.intensity.value]
    
    db.commit()
    db.refresh(log)
    return log

@router.delete("/{log_id}")
def delete_fitness_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = db.query(FitnessLog).filter(
        FitnessLog.id == log_id,
        FitnessLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Fitness log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Fitness log deleted successfully"}

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

@router.get("/monthly", response_model=MonthlyFitnessResponse)
def get_monthly_fitness(
    year: int = Query(default=None, description="Year (default: current year)"),
    month: int = Query(default=None, ge=1, le=12, description="Month (default: current month)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month
    
    _, last_day = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    
    logs = db.query(FitnessLog).filter(
        FitnessLog.user_id == current_user.id,
        FitnessLog.log_date >= start_date,
        FitnessLog.log_date <= end_date
    ).all()
    
    if not logs:
        return MonthlyFitnessResponse(
            year=year, month=month,
            total_steps=0, total_minutes=0,
            days_active=0, avg_daily_steps=0
        )
    
    total_steps = sum(log.steps for log in logs)
    total_minutes = sum(log.minutes_exercised for log in logs)
    days_active = sum(1 for log in logs if log.activity_completed)
    avg_daily_steps = total_steps / days_active if days_active > 0 else 0
    
    return MonthlyFitnessResponse(
        year=year, month=month,
        total_steps=total_steps,
        total_minutes=total_minutes,
        days_active=days_active,
        avg_daily_steps=round(avg_daily_steps, 0)
    )
