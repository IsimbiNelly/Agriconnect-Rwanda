from fastapi import Header, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from services.auth.register import create_farmer
from schemas.application_schema import FarmersRegistration
from database.session import get_db

router = APIRouter(
    prefix="/farmer_auth",
    tags=["Farmer auth management"]
    )

@router.post("/create")
async def create(farmer_payload:FarmersRegistration, db:Session = Depends(get_db)):
    """This route registers a new user"""
    return create_farmer(db=db, payload=farmer_payload)
