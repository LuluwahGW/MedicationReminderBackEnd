from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Reminder
from utils import get_db
from reminder_schema import ReminderCreate, ReminderRead
from utils import get_current_user

router = APIRouter(prefix="/reminders",tags=["Reminders"])


@router.post("/",response_model=ReminderRead)
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_reminder = Reminder(
        medication_id = reminder.medication_id,
        user_id = current_user.id,
        name = reminder.name,
        reminder_time = reminder.reminder_time,
        frequency = reminder.frequency,
        message = reminder.message
    )
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)
    return new_reminder

@router.get("/", response_model=List[ReminderRead])
def get_reminders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Reminder).filter(Reminder.user_id == current_user.id).all()
