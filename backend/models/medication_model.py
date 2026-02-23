from sqlalchemy import Column, Integer, String, Time, Enum as SQLEnum, ForeignKey
from database import Base
import enum
class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    dosage = Column(String(50))
    frequency_per_day = Column(Integer, default=1)
    reminder_time = Column(Time)