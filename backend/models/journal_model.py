from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, DECIMAL, ForeignKey
from datetime import datetime
from database import Base
class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    sentiment_score = Column(DECIMAL(4,3))  # -1.0 to 1.0
    emotion_label = Column(String(50))
    risk_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)