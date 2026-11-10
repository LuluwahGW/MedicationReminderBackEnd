import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# SQLite by default so the project runs with zero setup; override with a
# Postgres/MySQL URL in .env for a real deployment.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medications_db.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def upgrade_legacy_sqlite(bind=engine):
    """Add columns introduced after a SQLite file was first created.

    `create_all` never alters existing tables, so an older local database would
    break on the new `caregivers.status` column. Rows that already exist get
    PENDING: caregiver links made before consent existed must be accepted by the
    caregiver before they grant access. (Other databases: use real migrations.)
    """
    if bind.dialect.name != "sqlite":
        return
    inspector = inspect(bind)
    if "caregivers" not in inspector.get_table_names():
        return
    columns = {c["name"] for c in inspector.get_columns("caregivers")}
    if "status" not in columns:
        with bind.begin() as conn:
            conn.execute(text(
                "ALTER TABLE caregivers ADD COLUMN status VARCHAR(8) NOT NULL DEFAULT 'PENDING'"
            ))
