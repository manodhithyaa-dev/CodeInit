from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from datetime import datetime
from database import Base
import enum
class PrimaryGoal(str, enum.Enum):
    MOOD = "MOOD"
    MEDICATION = "MEDICATION"
    FITNESS = "FITNESS"
    STRESS = "STRESS"
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True)
    password = Column(String(255))
    name = Column(String(100))
    age_range = Column(String(20))
    primary_goal = Column(SQLEnum(PrimaryGoal), default=PrimaryGoal.MOOD)
    created_at = Column(DateTime, default=datetime.utcnow)