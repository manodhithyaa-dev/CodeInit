from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.medication_model import Medication
from models.medication_log_model import MedicationLog
from schemas.medication_schema import (
    MedicationCreate, MedicationResponse, 
    MedicationTakenRequest, MedicationSummaryResponse,
    MedicationUpdate
)
from typing import List, Optional
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
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Medication).filter(Medication.user_id == current_user.id)
    
    if search:
        query = query.filter(Medication.name.ilike(f"%{search}%"))
    
    total = query.count()
    offset = (page - 1) * limit
    
    medications = query.offset(offset).limit(limit).all()
    return medications

@router.get("/{medication_id}", response_model=MedicationResponse)
def get_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    ).first()
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    return medication

@router.put("/{medication_id}", response_model=MedicationResponse)
def update_medication(
    medication_id: int,
    medication: MedicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    ).first()
    
    if not db_medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    if medication.name is not None:
        db_medication.name = medication.name
    if medication.dosage is not None:
        db_medication.dosage = medication.dosage
    if medication.frequency_per_day is not None:
        db_medication.frequency_per_day = medication.frequency_per_day
    if medication.reminder_time is not None:
        db_medication.reminder_time = medication.reminder_time
    
    db.commit()
    db.refresh(db_medication)
    return db_medication

@router.delete("/{medication_id}")
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    ).first()
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    db.query(MedicationLog).filter(
        MedicationLog.medication_id == medication_id
    ).delete()
    
    db.delete(medication)
    db.commit()
    
    return {"message": "Medication deleted successfully"}

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
        raise HTTPException(status_code=404, detail="Medication not found")
    
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
