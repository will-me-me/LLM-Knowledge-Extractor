import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL","postgresql://myroot:root@postgres/mydatabase")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create tables
# Base.metadata.create_all(bind=engine)