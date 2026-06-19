from pydantic import BaseModel

class MotivationTextBase(BaseModel):
    message_text : str

class MotivationTextCreate(MotivationTextBase):
    pass

class MotivationTextOut(MotivationTextBase):
    message_id : int   #based on the same table in db

    class Config:
        orm_mode = True
