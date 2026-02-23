from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.user_model import User
from models.circle_model import SupportCircle
from models.circle_member_model import CircleMember, Role
from models.message_model import EncouragementMessage
from schemas.circle_schema import (
    CircleCreate, CircleResponse, CircleWithMembers,
    CircleMemberResponse, MessageCreate, MessageResponse,
    CircleUpdate
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

@router.get("/{circle_id}", response_model=CircleResponse)
def get_circle(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    
    is_member = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this circle")
    
    return circle

@router.put("/{circle_id}", response_model=CircleResponse)
def update_circle(
    circle_id: int,
    circle: CircleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not db_circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    
    if db_circle.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can update the circle")
    
    if circle.name is not None:
        db_circle.name = circle.name
    
    db.commit()
    db.refresh(db_circle)
    return db_circle

@router.post("/{circle_id}/join")
def join_circle(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    
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

@router.post("/{circle_id}/leave")
def leave_circle(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    
    membership = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="You are not a member of this circle")
    
    if circle.created_by == current_user.id:
        raise HTTPException(status_code=400, detail="Owner cannot leave the circle. Delete it instead.")
    
    db.delete(membership)
    db.commit()
    
    return {"message": "Left circle successfully"}

@router.get("/{circle_id}/members", response_model=CircleWithMembers)
def get_circle_members(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    
    members = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id
    ).all()
    
    return CircleWithMembers(
        id=circle.id,
        name=circle.name,
        created_by=circle.created_by,
        members=[CircleMemberResponse(id=m.id, user_id=m.user_id, role=m.role.value) for m in members]
    )

@router.delete("/{circle_id}/members/{user_id}")
def remove_circle_member(
    circle_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    
    if circle.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can remove members")
    
    membership = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")
    
    db.delete(membership)
    db.commit()
    
    return {"message": "Member removed successfully"}

@router.get("/{circle_id}/messages", response_model=List[MessageResponse])
def get_circle_messages(
    circle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    
    is_member = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this circle")
    
    messages = db.query(EncouragementMessage).filter(
        EncouragementMessage.circle_id == circle_id
    ).order_by(EncouragementMessage.created_at.desc()).all()
    
    return messages

@router.post("/{circle_id}/message", response_model=MessageResponse)
def send_message(
    circle_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    circle = db.query(SupportCircle).filter(SupportCircle.id == circle_id).first()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")
    
    is_member = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this circle")
    
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
