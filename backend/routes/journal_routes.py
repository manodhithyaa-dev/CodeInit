from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.journal_model import JournalEntry
from schemas.journal_schema import JournalCreate, JournalResponse, JournalAnalysisResponse
from ml.sentiment import analyze_sentiment, check_risk_keywords
from typing import List
from decimal import Decimal

router = APIRouter(prefix="/journal", tags=["Journal"])

@router.post("", response_model=JournalAnalysisResponse)
def create_journal_entry(
    journal: JournalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Use ML sentiment analysis module
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id
    ).order_by(JournalEntry.created_at.desc()).all()
    return entries
