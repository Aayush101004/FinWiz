import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# THE FIX: Using the correct username and password as defined in docker-compose.yml
SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@db/mydatabase"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


