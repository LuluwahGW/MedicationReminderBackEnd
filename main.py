from fastapi import FastAPI, Depends, HTTPException
from enum import Enum
from pydantic import BaseModel
import models
from database import engine, Base , SessionLocal
from sqlalchemy.orm import Session



#creating table based on models
Base.metadata.create_all(bind=engine)


app = FastAPI()


def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created!")



if __name__ == "__main__":
    create_tables()
    

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users")
def create_user(email: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=400,detail="Email has already been used")

    new_user = models.User(email=email, password=password)
    db.add(new_user)
    db.commit
    db.refresh(new_user)
    return{"id ": new_user.id, "email: ":new_user.email}


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id== user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    return{"id": user.id, "email": user.email}

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return[{"id": u.id, "email": u.email}for u in users]    


