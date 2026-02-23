from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user_model import User
from schemas.user_schema import UserCreate, UserLogin, TokenResponse
from utils.security import hash_password, verify_password, create_access_token
def register_user(user: UserCreate, db: Session):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=user.email,
        password=hash_password(user.password),
        name=user.name,
        age_range=user.age_range,
        primary_goal=user.primary_goal
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": new_user.email, "user_id": new_user.id})
    return TokenResponse(
        token=token,
        user=new_user
    )
def login_user(user: UserLogin, db: Session):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email, "user_id": db_user.id})
    return TokenResponse(
        token=token,
        user=db_user
    )