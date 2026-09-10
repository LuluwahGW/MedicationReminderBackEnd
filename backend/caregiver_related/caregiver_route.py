from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # type: ignore[import]
from database_utilis_related.utils import get_db, get_current_user
import database_utilis_related.models as models 
from caregiver_related import caregiver_schema
from medications_related import medication_schema

router = APIRouter(prefix="/caregivers",tags=["Caregivers"])

#comment

@router.post("/assign", response_model=caregiver_schema.CareGiverCreate)
def assign_caregiver(
    caregiver_data:caregiver_schema.CareGiverCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    if caregiver_data.cg_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot assign yourself as your own caregiver")

    caregiver_user = db.query(models.User).filter_by(id=caregiver_data.cg_id).first()
    if not caregiver_user:
        raise HTTPException(status_code=404, detail="Caregiver user not found")

    
    existing = db.query(models.CareGiver).filter_by(user_id=current_user.id, cg_id=caregiver_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Caregiver already assigned")

    new_caregiver = models.CareGiver(user_id=current_user.id, cg_id=caregiver_user.id)
    db.add(new_caregiver)
    db.commit()
    db.refresh(new_caregiver)
    return new_caregiver


@router.delete("/{caregiver_id}")
def remove_caregiver(
    caregiver_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    link = db.query(models.CareGiver).filter_by(user_id=current_user.id, cg_id=caregiver_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Caregiver assignment not found")

    db.delete(link)
    db.commit()
    return {"detail": "Caregiver removed successfully"}




@router.get("/me/patients", response_model=list[caregiver_schema.PatientWithMedications])
def get_my_patients_with_medications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    caregiver_links = db.query(models.CareGiver).filter_by(cg_id=current_user.id).all()
    if not caregiver_links:
        return []

    patients_with_meds = []
    for link in caregiver_links:
        patient = db.query(models.User).filter_by(id=link.user_id).first()
        if patient:
            medications = db.query(models.Medication).filter_by(user_id=patient.id, archived=False).all()
            patients_with_meds.append({
                "patient_id": patient.id,
                "patient_email": patient.email,
                "medications": medications
            })

    return patients_with_meds


@router.get("/patients/{patient_id}/medications", response_model=list[medication_schema.MedicationOut])
def get_patient_medications(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    link = db.query(models.CareGiver).filter_by(user_id=patient_id, cg_id=current_user.id).first()
    if not link:
        raise HTTPException(status_code=403, detail="Not authorized to view this patient's medications")

    medications = db.query(models.Medication).filter_by(user_id=patient_id, archived=False).all()
    return medications
