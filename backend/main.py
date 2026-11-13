import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import database_utilis_related.models as models
from database_utilis_related.database import engine, Base, SessionLocal, upgrade_legacy_sqlite
from database_utilis_related.utils import (
    verify_password,
    create_access_token,
    get_db,
    get_current_user,
)
from caregiver_related import caregiver_route as caregiverRoute
from medications_related import medication_route as medicationRoute
from reminders_related import reminders_route as remindersRoute
from user_related import user_routes as userRoute
from motivationtext_related import motivationtext_route as motiveRoute


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and load the canonical motivation quotes from JSON so a
    # fresh clone is ready to run with no manual seeding step.
    Base.metadata.create_all(bind=engine)
    upgrade_legacy_sqlite(engine)
    db = SessionLocal()
    try:
        added = motiveRoute.load_quotes_into_db(db)
        if added:
            print(f"Loaded {added} motivation quote(s) from file.")
    finally:
        db.close()
    yield


app = FastAPI(title="Medication Reminder API", lifespan=lifespan)

def _csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# Browser origins allowed to call the API. Local dev defaults; set CORS_ORIGINS on the
# host (comma-separated, e.g. your Lovable site URL) to allow a deployed frontend.
# CORS_ORIGIN_REGEX optionally matches many origins (e.g. Lovable preview URLs).
origins = _csv_env("CORS_ORIGINS", ["http://127.0.0.1:5500", "http://localhost:5500"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX") or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(userRoute.router)
app.include_router(remindersRoute.router)
app.include_router(medicationRoute.router)
app.include_router(caregiverRoute.router)
app.include_router(motiveRoute.router)


@app.get("/health", tags=["Health"])
def read_root():
    return {"status": "ok", "service": "Medication Reminder API"}


def authenticate_user(email: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


@app.post("/login", tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_email": user.email,
    }


@app.get("/me", tags=["Auth"])
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "name": current_user.name}


# Optionally serve a bundled frontend from the same app. Point FRONTEND_DIR at a folder
# containing index.html (e.g. archive/frontend-vanilla) to turn it on. The default folder
# no longer exists (the vanilla frontend is archived), so the backend runs as an API only.
# Mounted last so every API route above takes precedence over static files.
FRONTEND_DIR = Path(os.getenv("FRONTEND_DIR") or Path(__file__).resolve().parent.parent / "frontend")
if not FRONTEND_DIR.is_absolute():
    FRONTEND_DIR = (Path.cwd() / FRONTEND_DIR).resolve()

if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    @app.get("/", tags=["Health"], include_in_schema=False)
    def api_root():
        return {"status": "ok", "service": "Medication Reminder API", "docs": "/docs"}
