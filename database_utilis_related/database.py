from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

#checking if db exists, if not making one
DATABASE_URL = "mysql+mysqlconnector://root:root@localhost/medications_db"

#connecting db to file
engine = create_engine(DATABASE_URL,echo=True)

#creating a session factory?
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

#base class for models to inherit
Base = declarative_base()