from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal
from user_schema import UserResponse,UserCreate, UserLogin
from utils import hash_password, verify_password

router = APIRouter(prefix="/users",tags=["User"])

#depedency to get db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/login", response_model=UserResponse)
def login_user(user_login : UserLogin, db : Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="invalid email or passoword")
    
    if not verify_password(user_login.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return user


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
