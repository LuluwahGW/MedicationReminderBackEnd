from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal
from user_schema import UserResponse,UserCreate
import bcrypt

router = APIRouter(prefix="/users",tags=["User"])

#depedency to get db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/",response_model=UserResponse)
def create_user(user: UserCreate, db : Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400,detail="Email already has been used")
    hashed_password = bcrypt.hash(user.password)
    new_user = User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit
    db.refresh(new_user)
    return new_user
