from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserCreate(BaseModel):
    email : EmailStr
    password : str

class UserResponse(BaseModel):
    id : int
    email: EmailStr
    

class Config:
    orm_mode = True     

class UserLogin(BaseModel):
    email : EmailStr 
    password : str      

class LoginSchema(BaseModel):
    email: str
    password: str

