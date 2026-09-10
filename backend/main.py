from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import database_utilis_related.models as models
from database_utilis_related.database import engine, Base, SessionLocal
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
    db = SessionLocal()
    try:
        added = motiveRoute.load_quotes_into_db(db)
        if added:
            print(f"Loaded {added} motivation quote(s) from file.")
    finally:
        db.close()
    yield


app = FastAPI(title="Medication Reminder API", lifespan=lifespan)

# Frontend origins allowed to call the API (Live Server defaults).
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(userRoute.router)
app.include_router(remindersRoute.router)
app.include_router(medicationRoute.router)
app.include_router(caregiverRoute.router)
app.include_router(motiveRoute.router)


@app.get("/", tags=["Health"])
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
