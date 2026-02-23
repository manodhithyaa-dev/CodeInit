from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from schemas.user_schema import UserResponse, UserUpdate
from utils.security import hash_password

router = APIRouter(prefix="/users", tags=["User"])

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.age_range is not None:
        current_user.age_range = user_update.age_range
    if user_update.primary_goal is not None:
        current_user.primary_goal = user_update.primary_goal
    if user_update.password is not None:
        current_user.password = hash_password(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/me")
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Delete user's data first
    from models.journal_model import JournalEntry
    from models.medication_model import Medication
    from models.medication_log_model import MedicationLog
    from models.fitness_log_model import FitnessLog
    from models.circle_model import SupportCircle
    from models.circle_member_model import CircleMember
    from models.message_model import EncouragementMessage
    
    user_id = current_user.id
    
    db.query(JournalEntry).filter(JournalEntry.user_id == user_id).delete()
    
    medications = db.query(Medication).filter(Medication.user_id == user_id).all()
    for med in medications:
        db.query(MedicationLog).filter(MedicationLog.medication_id == med.id).delete()
    db.query(Medication).filter(Medication.user_id == user_id).delete()
    
    db.query(FitnessLog).filter(FitnessLog.user_id == user_id).delete()
    
    memberships = db.query(CircleMember).filter(CircleMember.user_id == user_id).all()
    for membership in memberships:
        circle = db.query(SupportCircle).filter(SupportCircle.id == membership.circle_id).first()
        if circle and circle.created_by == user_id:
            db.query(EncouragementMessage).filter(EncouragementMessage.circle_id == circle.id).delete()
            db.query(CircleMember).filter(CircleMember.circle_id == circle.id).delete()
            db.delete(circle)
        else:
            db.delete(membership)
    
    db.query(EncouragementMessage).filter(
        (EncouragementMessage.sender_id == user_id) | 
        (EncouragementMessage.receiver_id == user_id)
    ).delete()
    
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}
