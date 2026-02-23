from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey
from database import Base
class MedicationLog(Base):
    __tablename__ = "medication_logs"
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    taken_date = Column(Date, nullable=False)
    taken = Column(Boolean, default=False)