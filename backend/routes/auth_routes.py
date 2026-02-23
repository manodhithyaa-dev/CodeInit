from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from controllers.auth_controller import register_user, login_user
from schemas.user_schema import UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(user, db)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(user, db)