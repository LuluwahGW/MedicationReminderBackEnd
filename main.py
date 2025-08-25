from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
import models
from database import engine, Base , SessionLocal
from sqlalchemy.orm import Session
from user_routes import router as user_router
from utils import(verify_password,create_access_token,verify_token,oauth_scheme)
import reminders_route, medication_route


#creating table based on models
Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(user_router)
app.include_router(reminders_route.router)
app.include_router(medication_route.router)



#Base.metadata.drop_all(bind=engine)
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



@app.get("/")
def read_root():
    return {"message": "Welcome to this website"}


@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return[{"id": u.id, "email": u.email}for u in users]    


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id== user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    return{"id": user.id, "email": user.email}



@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
    "access_token": access_token,
    "token_type": "bearer",
    "user_email": user.email,
            }




def authenticate_user(email: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password):  # or user.hashed_password, check model
        return None
    return user



async def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    user_id = verify_token(token)
    try:
        user_id = int(user_id)
    except Exception:
        pass

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user



@app.get("/protected-route")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": f"Hello user {current_user.email}, you are authenticated :D"}



