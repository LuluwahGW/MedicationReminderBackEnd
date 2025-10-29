from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func #random function
import database_utilis_related.models as models 
from database_utilis_related.utils import get_current_user, get_db
from . import motivationtext_schema

router = APIRouter(prefix="/motivation", tags= ["Motivation"])

@router.get("/random",response_model=str) #response_model returns a string better than msg id (simpler for frontend)
def get_random_motivetext(db: Session = Depends(get_db)):
    random_text = db.query(models.MotivationText).order_by(func.random()).first()
    
    if not random_text:
        raise HTTPException(status_code=404, detail="MotivationText not found")
    
    return random_text.message_text

@router.post("/",response_model=motivationtext_schema.MotivationTextOut)
def create_motive_text(text : motivationtext_schema.MotivationTextCreate, db : Session = Depends(get_db), current_user : models.User = Depends(get_current_user)):
    new_text = models.MotivationText(message_text = text.message_text)  #based on table in db

    db.add(new_text)
    db.commit()
    db.refresh(new_text)

    return new_text

