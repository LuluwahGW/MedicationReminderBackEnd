from pydantic import BaseModel, field_validator, ValidationInfo
from datetime import datetime

class MedicationBase(BaseModel):
    name : str
    dosage : str
    start_date : datetime
    end_date : datetime
    archived : bool = False
    


class MedicationCreate(BaseModel):
    name : str
    dosage : str
    start_date : datetime
    end_date : datetime
    archived : bool = False


class MedicationUpdate(BaseModel):
    name: str | None = None
    dosage: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    archived: bool | None = None

class MedicationOut(MedicationBase):
    id : int
    user_id : int
    archived : bool

class Config:
    orm_mode = True
    from_attributes = True

    