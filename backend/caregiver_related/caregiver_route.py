import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # type: ignore[import]
from database_utilis_related.utils import get_db, get_current_user
import database_utilis_related.models as models
from database_utilis_related.models import CaregiverStatus
from caregiver_related import caregiver_schema
from medications_related import medication_schema

router = APIRouter(prefix="/caregivers", tags=["Caregivers"])

INVITE_LINK_TTL = timedelta(days=7)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _aware(dt: datetime) -> datetime:
    # SQLite hands datetimes back naive; everything we store is UTC.
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# --- Patient side: list / cancel or remove ---------------------------------

@router.get("/me", response_model=list[caregiver_schema.MyCaregiverOut])
def get_my_caregivers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Caregivers I invited, both pending and accepted."""
    links = db.query(models.CareGiver).filter_by(user_id=current_user.id).all()
    return [
        {
            "id": link.id,
            "cg_id": link.cg_id,
            "caregiver_name": link.caregiver.name,
            "caregiver_email": link.caregiver.email,
            "status": link.status,
        }
        for link in links
    ]


@router.delete("/{caregiver_id}")
def remove_caregiver(
    caregiver_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Cancel a pending invitation or remove an accepted caregiver (by their user id)."""
    link = db.query(models.CareGiver).filter_by(user_id=current_user.id, cg_id=caregiver_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Caregiver assignment not found")

    db.delete(link)
    db.commit()
    return {"detail": "Caregiver removed successfully"}


# --- Invite links: patient creates one, caregiver opens it and accepts ------

@router.post("/invite-links", response_model=caregiver_schema.InviteLinkOut)
def create_invite_link(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Make a single-use link (valid 7 days) to give to a prospective caregiver.

    The raw token is returned once and never stored; only its hash is kept.
    """
    token = secrets.token_urlsafe(32)
    invite = models.CaregiverInvite(
        patient_id=current_user.id,
        token_hash=_hash_token(token),
        expires_at=datetime.now(timezone.utc) + INVITE_LINK_TTL,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return {"token": token, "expires_at": invite.expires_at}


def _usable_invite(db: Session, token: str) -> models.CaregiverInvite:
    invite = db.query(models.CaregiverInvite).filter_by(token_hash=_hash_token(token)).first()
    if not invite:
        raise HTTPException(status_code=404, detail="This invite link is not valid")
    if invite.used_at is not None:
        raise HTTPException(status_code=410, detail="This invite link has already been used")
    if _aware(invite.expires_at) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="This invite link has expired")
    return invite


@router.get("/invite-links/{token}", response_model=caregiver_schema.InvitePreviewOut)
def preview_invite_link(
    token: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Who is inviting me? (Requires sign-in; changes nothing.)"""
    invite = _usable_invite(db, token)
    if invite.patient_id == current_user.id:
        raise HTTPException(status_code=400, detail="This is your own invite link - send it to someone else")
    return {
        "patient_name": invite.patient.name,
        "patient_email": invite.patient.email,
        "expires_at": invite.expires_at,
    }


@router.post("/invite-links/{token}/accept", response_model=caregiver_schema.CareGiverOut)
def accept_invite_link(
    token: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Become this patient's caregiver. The explicit click on this call is the consent."""
    invite = _usable_invite(db, token)
    if invite.patient_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot be your own caregiver")

    link = db.query(models.CareGiver).filter_by(user_id=invite.patient_id, cg_id=current_user.id).first()
    if link and link.status == CaregiverStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="You are already this patient's caregiver")
    if link:  # a legacy PENDING link (made before invite links existed) is answered by this one
        link.status = CaregiverStatus.ACCEPTED
    else:
        link = models.CareGiver(
            user_id=invite.patient_id, cg_id=current_user.id, status=CaregiverStatus.ACCEPTED
        )
        db.add(link)
    invite.used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(link)
    return link


# --- Caregiver views: accepted links only ----------------------------------

@router.get("/me/patients", response_model=list[caregiver_schema.PatientWithMedications])
def get_my_patients_with_medications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    caregiver_links = db.query(models.CareGiver).filter_by(
        cg_id=current_user.id, status=CaregiverStatus.ACCEPTED
    ).all()

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
    link = db.query(models.CareGiver).filter_by(
        user_id=patient_id, cg_id=current_user.id, status=CaregiverStatus.ACCEPTED
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="Not authorized to view this patient's medications")

    medications = db.query(models.Medication).filter_by(user_id=patient_id, archived=False).all()
    return medications
