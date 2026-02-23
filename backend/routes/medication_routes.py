from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.medication_model import Medication
from models.medication_log_model import MedicationLog
from schemas.medication_schema import (
    MedicationCreate, MedicationResponse, 
    MedicationTakenRequest, MedicationSummaryResponse
)
from typing import List
from datetime import date, timedelta

router = APIRouter(prefix="/medications", tags=["Medications"])

@router.post("", response_model=MedicationResponse)
def create_medication(
    medication: MedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_medication = Medication(
        user_id=current_user.id,
        name=medication.name,
        dosage=medication.dosage,
        frequency_per_day=medication.frequency_per_day,
        reminder_time=medication.reminder_time
    )
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)
    return db_medication

@router.get("", response_model=List[MedicationResponse])
def get_medications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Medication).filter(Medication.user_id == current_user.id).all()

@router.post("/{medication_id}/taken")
def mark_medication_taken(
    medication_id: int,
    data: MedicationTakenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    ).first()
    
    if not medication:
        return {"error": "Medication not found"}
    
    existing_log = db.query(MedicationLog).filter(
        MedicationLog.medication_id == medication_id,
        MedicationLog.taken_date == data.taken_date
    ).first()
    
    if existing_log:
        existing_log.taken = data.taken
    else:
        log = MedicationLog(
            medication_id=medication_id,
            user_id=current_user.id,
            taken_date=data.taken_date,
            taken=data.taken
        )
        db.add(log)
    
    db.commit()
    return {"message": "Updated successfully"}

@router.get("/summary", response_model=MedicationSummaryResponse)
def get_medication_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    medications = db.query(Medication).filter(
        Medication.user_id == current_user.id
    ).all()
    
    if not medications:
        return MedicationSummaryResponse(current_streak=0, weekly_adherence=0.0)
    
    medication_ids = [m.id for m in medications]
    total_freq = sum(m.frequency_per_day for m in medications)
    
    logs = db.query(MedicationLog).filter(
        MedicationLog.medication_id.in_(medication_ids),
        MedicationLog.taken_date >= week_ago,
        MedicationLog.taken == True
    ).all()
    
    doses_taken = len(logs)
    doses_scheduled = total_freq * 7
    weekly_adherence = round((doses_taken / doses_scheduled * 100), 2) if doses_scheduled > 0 else 0.0
    
    streak = 0
    check_date = today
    while True:
        day_logs = db.query(MedicationLog).filter(
            MedicationLog.medication_id.in_(medication_ids),
            MedicationLog.taken_date == check_date,
            MedicationLog.taken == True
        ).all()
        
        if len(day_logs) >= total_freq:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    return MedicationSummaryResponse(current_streak=streak, weekly_adherence=weekly_adherence)
