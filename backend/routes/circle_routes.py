from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.circle_model import SupportCircle
from models.circle_member_model import CircleMember, Role
from models.message_model import EncouragementMessage
from schemas.circle_schema import (
    CircleCreate, CircleResponse, CircleWithMembers,
    CircleMemberResponse, MessageCreate, MessageResponse
)
from typing import List

router = APIRouter(prefix="/circles", tags=["Support Circles"])

@router.post("", response_model=CircleResponse)
def create_circle(
    circle: CircleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_circle = SupportCircle(
        name=circle.name,
        created_by=current_user.id
    )
    db.add(db_circle)
    db.commit()
    db.refresh(db_circle)
    
    member = CircleMember(
        circle_id=db_circle.id,
        user_id=current_user.id,
        role=Role.OWNER
    )
    db.add(member)
    db.commit()
    
    return db_circle

@router.get("", response_model=List[CircleResponse])
def get_circles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle_ids = db.query(CircleMember.circle_id).filter(
        CircleMember.user_id == current_user.id
    ).subquery()
    
    return db.query(SupportCircle).filter(SupportCircle.id.in_(circle_ids)).all()

@router.post("/{circle_id}/join")
def join_circle(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not circle:
        return {"error": "Circle not found"}
    
    existing = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == current_user.id
    ).first()
    
    if existing:
        return {"message": "Already a member"}
    
    member = CircleMember(
        circle_id=circle_id,
        user_id=current_user.id,
        role=Role.MEMBER
    )
    db.add(member)
    db.commit()
    return {"message": "Joined successfully"}

@router.get("/{circle_id}/members", response_model=CircleWithMembers)
def get_circle_members(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not circle:
        return {"error": "Circle not found"}
    
    members = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id
    ).all()
    
    return CircleWithMembers(
        id=circle.id,
        name=circle.name,
        created_by=circle.created_by,
        members=[CircleMemberResponse(id=m.id, user_id=m.user_id, role=m.role.value) for m in members]
    )

@router.post("/{circle_id}/message", response_model=MessageResponse)
def send_message(
    circle_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_member = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        return {"error": "Not a member of this circle"}
    
    db_message = EncouragementMessage(
        circle_id=circle_id,
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
