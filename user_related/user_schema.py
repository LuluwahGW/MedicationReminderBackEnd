from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email : EmailStr
    password : str
    name : str


class UserResponse(BaseModel):
    name : str
    email: EmailStr
    

class Config:
    orm_mode = True     

class UserLogin(BaseModel):
    email : EmailStr 
    password : str      



