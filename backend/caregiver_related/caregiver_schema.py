from pydantic import BaseModel
from medications_related import medication_schema
from database_utilis_related.models import CaregiverStatus
from datetime import datetime
from typing import List

class UserInfo(BaseModel):
    id: int
    name : str
    email : str

class CareGiverBase(BaseModel):
    user_id : int
    cg_id : int

class CareGiverOut(CareGiverBase):
    id : int
    status : CaregiverStatus
    model_config = {"from_attributes": True}

class MyCaregiverOut(BaseModel):
    """A caregiver I invited, with whether they have accepted yet."""
    id : int
    cg_id : int
    caregiver_name : str | None
    caregiver_email : str
    status : CaregiverStatus

class InviteLinkOut(BaseModel):
    token : str
    expires_at : datetime

class InvitePreviewOut(BaseModel):
    """What the invited person sees before accepting."""
    patient_name : str | None
    patient_email : str
    expires_at : datetime

class PatientWithMedications(BaseModel):
    patient_id : int
    patient_email : str
    medications : List[medication_schema.MedicationOut]
    model_config = {"from_attributes": True}
