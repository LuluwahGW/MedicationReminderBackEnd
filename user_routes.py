from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import User
from utils import get_db
from user_schema import UserResponse,UserCreate, UserLogin
from utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/users",tags=["User"])




    


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already used")

    
    hashed_password = hash_password(user.password)

    
    new_user = User(email=user.email, password=hashed_password)

    db.add(new_user)
    db.commit()  
    db.refresh(new_user)

    return new_user
