from fastapi import Header, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from services.auth.register import create_buyer
from schemas.application_schema import Buyers
from database.session import get_db

router = APIRouter(
    prefix="/buyers_auth",
    tags=["Buyers auth management"]
    )

@router.post("/create")
async def create(payload:Buyers, db:Session = Depends(get_db)):
    """This route registers a new user"""
    return create_buyer(db=db, payload=payload)
