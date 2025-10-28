from fastapi import APIRouter, Depends, HTTPException , status
from sqlalchemy.orm import Session
from database_utilis_related.models import User, CareGiver
from database_utilis_related.utils import get_db , get_current_user
from .user_schema import UserResponse, UserCreate, UserUpdate
from database_utilis_related.utils import hash_password

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

@hello.patch("/me",response_model=UserResponse) #using /me path due to security reasons + current user for authorization
def update_user(user_update : UserUpdate, db : Session = Depends(get_db),CU : User = Depends(get_current_user)):
    if user_update.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()

        if existing_user and existing_user.id != CU.id:
            raise HTTPException(status_code=400,detail="Email already registered")
        
    for key , value in user_update.model_dump(exclude_unset=True).items():
        setattr(CU, key, value)    

    db.commit()
    db.refresh(CU)
    return CU    

@hello.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    #deleting links to any caregiver
    db.query(CareGiver).filter(
        (CareGiver.user_id == current_user.id) |
        (CareGiver.cg_id == current_user.id)
    ).delete(synchronize_session=False) 

    db.delete(current_user)
    db.commit()

    return 