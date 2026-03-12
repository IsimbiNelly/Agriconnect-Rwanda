#!/usr/bin/env python3

from .base import Base
from .create_session import engine

from model import database_model

def create_tables():
    print("Creating database tables...")
    print("Registered tables:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
