from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel
import models
from database import engine, Base , SessionLocal

from database import SessionLocal


print(Base.metadata.tables.keys())

print("Tables registered:", Base.metadata.tables.keys())


#creating table based on models
Base.metadata.create_all(bind=engine)


#app = FastAPI()


def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created!")



if __name__ == "__main__":
    create_tables()
    



print(Base.metadata.tables.keys())





