#!/usr/bin/env python3

from .http_status_code import NotFound, BadRequest

class CRUDService:
    """A generic CRUD service for any SQLAlchemy model"""
    
    def __init__(self, db, model):
        self.db = db
        self.model = model

    # Create
    def create(self, payload: dict):

        """Create a new instance of the model with the given payload"""
        
        instance = self.model(**payload)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    # Read by ID (assuming 'id' or 'experience_id' etc.)
    def get(self, id_field: str, value: str):
        """Get an instance by its ID field and value"""

        instance = self.db.query(self.model).filter(getattr(self.model, id_field) == value).first()
        if not instance:
            raise NotFound(f"{self.model.__name__} not found")
        return instance

    # Update
    def update(self, id_field: str, value: str, payload: dict):
        """Update an instance by its ID field and value"""

        instance = self.get(id_field, value)
        for key, val in payload.items():
            setattr(instance, key, val)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    # Delete
    def delete(self, id_field: str, value: str):
        """Delete an instance by its ID field and value"""

        instance = self.get(id_field, value)
        self.db.delete(instance)
        self.db.commit()
        return {"message": f"{self.model.__name__} deleted successfully"}
