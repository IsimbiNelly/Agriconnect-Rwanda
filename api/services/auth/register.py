import bcrypt

from sqlalchemy.orm import Session

from datetime import datetime, timezone

from model.database_model import Farmer, FarmerInformation, Buyer
from schemas.application_schema import FarmersRegistration, FarmersMoreInformation, Buyers
from utils.crud_handler import CRUDService

def create_farmer(db:Session, payload:FarmersRegistration):
    """
    this function handles farmers registration
    """
    crud_handler = CRUDService(db=db, model=Farmer)
    data = payload.model_dump(mode="json")
    data.pop("role", None)
    data["password"] = bcrypt.hashpw(
        data["password"].encode("utf-8"),
        bcrypt.gensalt()
        ).decode("utf-8")
    data["created_at"] = datetime.now(timezone.utc)
    data["updated_at"] = datetime.now(timezone.utc)
    try:
        user_registration = crud_handler.create(payload=data)
    except Exception as database_error:
        raise Exception(f"An error occured!:\n {database_error}")
    
    return {
        "status":"Success",
        "data":user_registration
    }

def create_buyer(db: Session, payload: Buyers):
    """This function handles buyers registration"""
    crud_handler = CRUDService(db=db, model=Buyer)
    data = payload.model_dump(mode="json")
    
    # Hash password
    data["password"] = bcrypt.hashpw(
        data["password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    data.pop("role", None)

    # Proper datetime objects
    data["created_at"] = datetime.now(timezone.utc)
    data["updated_at"] = datetime.now(timezone.utc)
    
    try:
        user_registration = crud_handler.create(payload=data)
    except Exception as database_error:
        raise Exception(f"An error occured!:\n {database_error}")
    
    return {
        "status": "Success",
        "data": user_registration
    }
