from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models,medication_schema
from utils import get_db

router = APIRouter(prefix="/medications",tags=["Medications"])


@router.post("/",response_model=medication_schema.MedicationOut)
def create_medication(med : medication_schema.MedicationCreate, db : Session = Depends(get_db)):
    new_med  = models.Medication(**med.model_dump())

    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med

@router.get("/users/{user_id}",response_model=list[medication_schema.MedicationOut])
def list_medications(user_id : int, db: Session = Depends(get_db)):
    meds = db.query(models.Medication).filter(models.Medication.user_id == user_id).all()
    return meds

@router.get("/{med_id}", response_model=medication_schema.MedicationOut)
def get_medication(med_id : int, db : Session = Depends(get_db)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404,detail="Medication Not Found")
    return med

@router.put("/{med_id}", response_model=medication_schema.MedicationOut)
def update_medication(med_id : int, med_update : medication_schema.MedicationUpdate, db : Session = Depends(get_db)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404,detail="Medication not Found")
    
    for key , value in med_update.model_dump(exclude_unset=True).items():
        setattr(med,key,value)

    db.commit()
    db.refresh(med)
    return med

@router.delete("/{med_id}",status_code= status.HTTP_204_NO_CONTENT)
def delete_medication(med_id : int, db : Session = Depends(get_db)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication Not Found")
    db.delete(med)
    db.commit()
    return {"detail":"Medication Deleted"}

