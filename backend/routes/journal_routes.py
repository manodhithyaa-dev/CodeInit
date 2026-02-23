from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.journal_model import JournalEntry
from schemas.journal_schema import JournalCreate, JournalResponse, JournalAnalysisResponse, JournalUpdate
from ml.sentiment import analyze_sentiment, check_risk_keywords
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

router = APIRouter(prefix="/journal", tags=["Journal"])

@router.post("", response_model=JournalAnalysisResponse)
def create_journal_entry(
    journal: JournalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = analyze_sentiment(journal.content)
    risk_flag = check_risk_keywords(journal.content) or analysis.get("risk_flag", False)
    
    db_entry = JournalEntry(
        user_id=current_user.id,
        content=journal.content,
        sentiment_score=Decimal(str(analysis["score"])),
        emotion_label=analysis["emotion"],
        risk_flag=risk_flag
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return JournalAnalysisResponse(
        sentiment_score=float(db_entry.sentiment_score),
        emotion_label=db_entry.emotion_label,
        risk_flag=db_entry.risk_flag
    )

@router.get("", response_model=List[JournalResponse])
def get_journal_entries(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in content"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    emotion: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(JournalEntry).filter(JournalEntry.user_id == current_user.id)
    
    if search:
        query = query.filter(JournalEntry.content.ilike(f"%{search}%"))
    
    if start_date:
        query = query.filter(JournalEntry.created_at >= start_date)
    
    if end_date:
        query = query.filter(JournalEntry.created_at <= end_date)
    
    if emotion:
        query = query.filter(JournalEntry.emotion_label == emotion)
    
    total = query.count()
    offset = (page - 1) * limit
    
    entries = query.order_by(JournalEntry.created_at.desc()).offset(offset).limit(limit).all()
    
    return entries

@router.get("/{entry_id}", response_model=JournalResponse)
def get_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    return entry

@router.put("/{entry_id}", response_model=JournalResponse)
def update_journal_entry(
    entry_id: int,
    journal: JournalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    if journal.content:
        analysis = analyze_sentiment(journal.content)
        risk_flag = check_risk_keywords(journal.content) or analysis.get("risk_flag", False)
        entry.content = journal.content
        entry.sentiment_score = Decimal(str(analysis["score"]))
        entry.emotion_label = analysis["emotion"]
        entry.risk_flag = risk_flag
    
    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/{entry_id}")
def delete_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    db.delete(entry)
    db.commit()
    
    return {"message": "Journal entry deleted successfully"}
