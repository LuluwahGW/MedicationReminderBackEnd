from fastapi import FastAPI, Depends, HTTPException, status  # type: ignore[import]
from fastapi.security.oauth2 import OAuth2PasswordRequestForm  # type: ignore[import]
import database_utilis_related.models as models
from database_utilis_related.database import engine, Base , SessionLocal
from sqlalchemy.orm import Session  # type: ignore[import]
from database_utilis_related.utils import(verify_password,create_access_token,verify_token,oauth_scheme)
from caregiver_related import caregiver_route as caregiverRoute
from medications_related import medication_route as medicationRoute
from reminders_related import reminders_route as remindersRoute
from user_related import user_routes as userRoute
from motivationtext_related import motivationtext_route as motiveRoute
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import] # connecting back-end with front-end (Cross-Origin-Resource-Sharing)

#creating table based on models
Base.metadata.create_all(bind=engine)


app = FastAPI()

origins=[
    #"http://localhost:3000", # react app (still not sure abt this)
    "http://127.0.0.1:5500" # live server VS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)



app.include_router(userRoute.hello)
app.include_router(remindersRoute.router)
app.include_router(medicationRoute.router)
app.include_router(caregiverRoute.router)
app.include_router(motiveRoute.router)



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



