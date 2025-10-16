from pydantic import BaseModel
from datetime import datetime
from database_utilis_related.models import FrequencyEnum





class ReminderBase(BaseModel):
    medication_id: int
    name: str
    reminder_time: datetime
    frequency: FrequencyEnum 
    message: str



    

class ReminderCreate(ReminderBase):
    pass



class ReminderRead(ReminderBase):
    id: int
    isTaken: bool
    created_at: datetime
    updated_at: datetime | None = None

class Config:
    orm_mode = True  
    use_enum_values = True  
