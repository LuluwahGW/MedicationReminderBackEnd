import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# SQLite by default so the project runs with zero setup; override with a
# Postgres/MySQL URL in .env for a real deployment.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medications_db.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
