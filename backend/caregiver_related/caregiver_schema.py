from pydantic import BaseModel
from medications_related import medication_schema
from typing import List

class UserInfo(BaseModel):
    id: int
    name : str
    email : str

class CareGiverBase(BaseModel):
    user_id : int
    cg_id : int

class CareGiverCreate(CareGiverBase):
    pass

class CareGiverOut(CareGiverBase):
    id : int
    model_config = {"from_attributes": True}

class PatientWithMedications(BaseModel):
    patient_id : int
    patient_email : str
    medications : List[medication_schema.MedicationOut]
    model_config = {"from_attributes": True}