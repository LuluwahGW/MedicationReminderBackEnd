from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status , Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt,ExpiredSignatureError
import os , database_utilis_related.models as models
from sqlalchemy.orm import Session
from database_utilis_related.database  import SessionLocal
from typing import Optional


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False)

def hash_password(password: str) -> str:
    truncated = password.encode("utf-8")[:72]
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(truncated, hashed_password)



SECRET_KEY = os.getenv("SECRET_KEY")  #9sF3b8Vx1QwZpL0TtXkHjN5YrCeRm7Ud
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token : str):
    try:
        payload = jwt.decode(token, str(SECRET_KEY) , algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


async def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    user_id = verify_token(token)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user