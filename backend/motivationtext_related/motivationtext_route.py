import json
from pathlib import Path
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func  # random function
import database_utilis_related.models as models
from database_utilis_related.utils import get_current_user, get_db
from . import motivationtext_schema

router = APIRouter(prefix="/motivation", tags=["Motivation"])

QUOTES_FILE = Path(__file__).parent / "motivation_quotes.json"


def load_quotes_into_db(db: Session) -> int:
    """Insert any quotes from motivation_quotes.json that aren't in the DB yet.

    The JSON file is the canonical source (committed to the repo); this keeps
    the DB in sync so a fresh clone is populated automatically on startup.
    Returns the number of quotes added.
    """
    try:
        with open(QUOTES_FILE, encoding="utf-8") as f:
            quotes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

    existing = {m.message_text for m in db.query(models.MotivationText).all()}
    added = 0
    for text in quotes:
        text = text.strip()
        if text and text not in existing:
            db.add(models.MotivationText(message_text=text))
            added += 1
    if added:
        db.commit()
    return added


@router.get("/random", response_model=str)  # simpler for the frontend than a msg id
def get_random_motivetext(db: Session = Depends(get_db)):
    random_text = db.query(models.MotivationText).order_by(func.random()).first()

    if not random_text:
        raise HTTPException(status_code=404, detail="MotivationText not found")

    return random_text.message_text


@router.post("/", response_model=motivationtext_schema.MotivationTextOut)
def create_motive_text(
    text: motivationtext_schema.MotivationTextCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_text = models.MotivationText(message_text=text.message_text)

    db.add(new_text)
    db.commit()
    db.refresh(new_text)

    return new_text
