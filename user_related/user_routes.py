from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database_utilis_related.models import User
from database_utilis_related.utils import get_db
from .user_schema import UserResponse,UserCreate, UserLogin
from database_utilis_related.utils import hash_password, verify_password, create_access_token

hello = APIRouter(prefix="/users",tags=["User"])


@hello.post("/register", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    
    new_user = User(
        email=user.email,
        password=hashed_password,
        name=user.name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
