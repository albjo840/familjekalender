import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Railway ger DATABASE_URL automatiskt
DATABASE_URL = os.getenv("DATABASE_URL")

# Om vi kör lokalt, använd en lokal databas
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/familjekalender"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
