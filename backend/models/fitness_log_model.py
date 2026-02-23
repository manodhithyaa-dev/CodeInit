from sqlalchemy import Column, Integer, Boolean, Date, Enum as SQLEnum, ForeignKey
from database import Base
import enum
class Intensity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
class FitnessLog(Base):
    __tablename__ = "fitness_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date = Column(Date, nullable=False)
    activity_completed = Column(Boolean, default=False)
    steps = Column(Integer, default=0)
    minutes_exercised = Column(Integer, default=0)
    intensity = Column(SQLEnum(Intensity), default=Intensity.LOW)