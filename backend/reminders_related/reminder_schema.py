from pydantic import BaseModel
from datetime import datetime
from database_utilis_related.models import FrequencyEnum





class ReminderBase(BaseModel): #base is input values that will produce an output (id in database bcz it hasnt been created)
    medication_id: int
    name: str
    reminder_time: datetime
    frequency: FrequencyEnum 
    message: str



    

class ReminderCreate(ReminderBase): #must be all values from args ReminderBase
    pass



class ReminderRead(ReminderBase):
    id: int
    isTaken: bool
    created_at: datetime
    updated_at: datetime | None = None  #could be no updates

class ReminderUpdate(ReminderBase): # | none could update a value or not
    medication_id: int | None = None
    name: str | None = None
    reminder_time: datetime | None = None
    frequency: FrequencyEnum | None = None
    message: str | None = None
    isTaken: bool | None = None
    model_config = {"from_attributes": True, "use_enum_values": True}  
