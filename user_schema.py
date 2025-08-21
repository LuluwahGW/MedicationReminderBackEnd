from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


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



