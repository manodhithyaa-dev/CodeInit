from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.journal_model import JournalEntry
from models.medication_model import Medication
from models.medication_log_model import MedicationLog
from models.fitness_log_model import FitnessLog
from datetime import date, datetime
from typing import Optional
import json

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/journal")
def export_journal(
    format: str = Query("json", regex="^(json|csv)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(JournalEntry).filter(JournalEntry.user_id == current_user.id)
    
    if start_date:
        query = query.filter(JournalEntry.created_at >= start_date)
    if end_date:
        query = query.filter(JournalEntry.created_at <= end_date)
    
    entries = query.order_by(JournalEntry.created_at.desc()).all()
    
    if format == "json":
        data = []
        for entry in entries:
            data.append({
                "id": entry.id,
                "content": entry.content,
                "sentiment_score": float(entry.sentiment_score) if entry.sentiment_score else None,
                "emotion_label": entry.emotion_label,
                "risk_flag": entry.risk_flag,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        return {
            "format": "json",
            "count": len(data),
            "data": data
        }
    
    # CSV format
    csv_lines = ["id,content,sentiment_score,emotion_label,risk_flag,created_at"]
    for entry in entries:
        content = entry.content.replace('"', '""')
        csv_lines.append(
            f'{entry.id},"{content}",{entry.sentiment_score or ""},{entry.emotion_label or ""},{entry.risk_flag},{entry.created_at or ""}'
        )
    
    return {
        "format": "csv",
        "count": len(entries),
        "data": "\n".join(csv_lines)
    }

@router.get("/medications")
def export_medications(
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    medications = db.query(Medication).filter(
        Medication.user_id == current_user.id
    ).all()
    
    med_ids = [m.id for m in medications]
    logs = []
    if med_ids:
        logs = db.query(MedicationLog).filter(
            MedicationLog.medication_id.in_(med_ids)
        ).order_by(MedicationLog.taken_date.desc()).all()
    
    if format == "json":
        meds_data = []
        for med in medications:
            med_logs = [l for l in logs if l.medication_id == med.id]
            meds_data.append({
                "id": med.id,
                "name": med.name,
                "dosage": med.dosage,
                "frequency_per_day": med.frequency_per_day,
                "reminder_time": med.reminder_time.isoformat() if med.reminder_time else None,
                "logs": [
                    {
                        "taken_date": log.taken_date.isoformat() if log.taken_date else None,
                        "taken": log.taken
                    }
                    for log in med_logs
                ]
            })
        return {
            "format": "json",
            "count": len(meds_data),
            "data": meds_data
        }
    
    # CSV format
    csv_lines = ["medication_id,medication_name,dosage,taken_date,taken"]
    for med in medications:
        med_logs = [l for l in logs if l.medication_id == med.id]
        if not med_logs:
            csv_lines.append(f'{med.id},{med.name},{med.dosage or ""},,')
        for log in med_logs:
            csv_lines.append(
                f'{med.id},{med.name},{med.dosage or ""},{log.taken_date},{log.taken}'
            )
    
    return {
        "format": "csv",
        "count": len(medications),
        "data": "\n".join(csv_lines)
    }

@router.get("/fitness")
def export_fitness(
    format: str = Query("json", regex="^(json|csv)$"),
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
    
    logs = query.order_by(FitnessLog.log_date.desc()).all()
    
    if format == "json":
        data = []
        for log in logs:
            data.append({
                "id": log.id,
                "log_date": log.log_date.isoformat() if log.log_date else None,
                "activity_completed": log.activity_completed,
                "steps": log.steps,
                "minutes_exercised": log.minutes_exercised,
                "intensity": log.intensity.value
            })
        return {
            "format": "json",
            "count": len(data),
            "data": data
        }
    
    # CSV format
    csv_lines = ["id,log_date,activity_completed,steps,minutes_exercised,intensity"]
    for log in logs:
        csv_lines.append(
            f'{log.id},{log.log_date},{log.activity_completed},{log.steps},{log.minutes_exercised},{log.intensity.value}'
        )
    
    return {
        "format": "csv",
        "count": len(logs),
        "data": "\n".join(csv_lines)
    }
