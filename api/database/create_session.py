#!/usr/bin/env python3

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get the directory where this file is located (database/)
BASE_DIR = Path(__file__).resolve().parent

# Create repositories folder inside database/
REPOSITORY_DIR = BASE_DIR / "repositories"
REPOSITORY_DIR.mkdir(parents=True, exist_ok=True)

# SQLite database path (replace with PostgreSQL URL in production)
DATABASE_URL = f"sqlite:///{REPOSITORY_DIR}/agriconnect.db"

if not DATABASE_URL:
    raise ValueError("Database not found. Check the .env file")

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
