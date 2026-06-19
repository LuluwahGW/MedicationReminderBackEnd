from pydantic import BaseModel, EmailStr, field_validator
import re


class UserCreate(BaseModel):
    email : EmailStr
    password : str
    name : str

    @field_validator('password')
    def validate_password(cls, v):
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters')
            if not re.search(r'[A-Z]', v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not re.search(r'[a-z]', v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one number')
            return v

class UserResponse(BaseModel):
    name : str
    email: EmailStr
    
class UserUpdate(BaseModel):
    name : str | None = None
    email: EmailStr | None = None
    
class Config:
    orm_mode = True     

class UserLogin(BaseModel):
    email : EmailStr 
    password : str      



