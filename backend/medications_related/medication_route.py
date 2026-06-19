from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import database_utilis_related.models as models
from database_utilis_related.utils import get_db, get_current_user
from database_utilis_related.models import User
from .medication_schema import MedicationCreate, MedicationOut, MedicationUpdate
router = APIRouter(prefix="/medications",tags=["Medications"])


@router.post("/",response_model=MedicationOut)
def create_medication(med : MedicationCreate, db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):

    existing = db.query(models.Medication).filter_by(
        user_id=current_user.id, name=med.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Medication '{med.name}' already exists."
        )

    new_med = models.Medication(
        user_id=current_user.id,
        name=med.name,
        dosage=med.dosage,
        archived=False
    )
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med

@router.get("/me",response_model=list[MedicationOut])
def list_medications(current_user : User = Depends(get_current_user), db: Session = Depends(get_db)):
    meds = db.query(models.Medication).filter(models.Medication.user_id == current_user.id, models.Medication.archived == False).all()
    return meds

@router.get("/archived",response_model=list[MedicationOut])
def list_archived_medications(current_user : User = Depends(get_current_user), db: Session = Depends(get_db)):
    meds = db.query(models.Medication).filter(models.Medication.user_id == current_user.id, models.Medication.archived == True).all()
    return meds

@router.get("/{med_id}", response_model=MedicationOut)
def get_medication(med_id : int, db : Session = Depends(get_db), include_archived : bool =False, current_user : User = Depends(get_current_user)):
    query = db.query(models.Medication).filter(models.Medication.user_id == current_user.id)

    if not query:
        raise HTTPException(status_code=404,detail="Medication Not Found")
    
    if not include_archived:
        query = query.filter(models.Medication.archived == False)

    return query.all()


@router.put("/{med_id}", response_model=MedicationOut)
def update_medication(med_id : int, med_update : MedicationUpdate, db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):

    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == current_user.id).first()
    
    if not med:
        raise HTTPException(status_code=404,detail="Medication not Found")
    
    for key , value in med_update.model_dump(exclude_unset=True).items():
        setattr(med,key,value)

    db.commit()
    db.refresh(med)
    return med
# delete put
@router.put("/archive/{med_id}", status_code=200)
def archive_medication(
    med_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    medication = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.user_id == current_user.id
    ).first()

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )

    medication.archived = True
    db.commit()
    return {"detail": f"Medication '{medication.name}' archived successfully"}




@router.delete("/{med_id}",status_code= status.HTTP_204_NO_CONTENT)
def delete_medication(med_id : int, db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == current_user.id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication Not Found")
    db.delete(med)
    db.commit()
    return {"detail":"Medication Deleted"}

