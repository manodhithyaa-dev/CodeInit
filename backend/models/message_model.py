from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from datetime import datetime
from database import Base
class EncouragementMessage(Base):
    __tablename__ = "encouragement_messages"
    id = Column(Integer, primary_key=True, index=True)
    circle_id = Column(Integer, ForeignKey("support_circles.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)