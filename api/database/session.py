#!/usr/bin/env python3

from .create_session import SessionLocal

def get_db():
    """This function manages session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close
