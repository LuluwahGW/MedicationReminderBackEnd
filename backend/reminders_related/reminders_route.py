from fastapi import APIRouter,Depends,HTTPException , status
from sqlalchemy.orm import Session
from typing import List
from database_utilis_related.models import Reminder
from database_utilis_related.utils import get_db
from .reminder_schema import ReminderCreate, ReminderRead, ReminderUpdate
from database_utilis_related.utils import get_current_user
import database_utilis_related.models as models


router = APIRouter(prefix="/reminders",tags=["Reminders"])

#create reminder for auth user (Depends get current user)
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

#get reminders from user id
@router.get("/{user_id}", response_model=List[ReminderRead])
def get_reminders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    return db.query(Reminder).filter(Reminder.user_id == current_user.id).all()

#update reminder (could e time or freq) patch --> updating certain fields 
@router.patch("/{reminder_id}", response_model=ReminderUpdate)
def update_reminders(reminder_id : int, reminder_update : ReminderUpdate, db : Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id, models.Reminder.user_id == current_user.id).first() #filtering reminder id from db

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    for key, value in reminder_update.model_dump(exclude_unset=True).items(): #exclude_unset is only taking the value that the user sent (all null values except time) + items makes it inot a list []
        setattr(reminder, key, value) #setting attributes values (reminder.message = "take with food")

    db.commit()
    db.refresh(reminder)
    return reminder  

@router.delete("/{reminder_id}")
def deleted_reminder(reminder_id : int, db: Session = Depends(get_db),current_user : models.User = Depends(get_current_user)):
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id, models.Reminder.user_id == current_user.id).first() #filtering reminder id from db

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    return {"detail":"reminder deleted successfully"}