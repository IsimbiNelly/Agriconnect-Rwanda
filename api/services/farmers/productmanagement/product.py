#!/usr/bin/env python3

from sqlalchemy.orm import Session
from model.database_model import ProductList, ProductImage
from schemas.application_schema import ProductList as product_list_schema
from schemas.application_schema import ProductImage as product_image_schema
from utils.crud_handler import CRUDService
from utils.http_status_code import NotFound

class ProductManagementService:
    def __init__(self, db:Session):
        self.db = db

    def get_all_products(self):
        """get all products"""
        all_products = self.db.query(ProductList).all()
        return all_products

    def get_products_for_farmer(self, farmer_id:str):
        """get products for particular farmer id"""
        all_products = self.db.query(ProductList).where(ProductList.farmer_id == farmer_id)

    def get_product(self, product_id):
        """get a specific product"""
        crud_handler = CRUDService(db=self.db, model=ProductList)
        return crud_handler.get("product_id", product_id)

    def create_product(self, payload:product_list_schema, farmer_id:int):
        """create a new product"""
        data = payload.model_dump(mode="json")
        data["farmer_id"] = farmer_id
        crud_handler = CRUDService(db=self.db, payload=payload)
        return crud_handler.create(payload=data)
    
    def update_product(self, farmer_id, product_id:str, product_payload:product_list_schema):
        """update product"""
        crud_handler = CRUDService(db=self.db, model=ProductList)
        product_detail = crud_handler.get("product_id", product_id)
        data = product_payload.model_dump(mode="json")
        data["farmer_id"] = farmer_id
        return crud_handler.update("product_id", product_id, product_id)
    
    def delete_product(self, product_id:str, farmer_id:int):
        crud_handler = CRUDService(db=self.db, model=ProductList)
        product_details = crud_handler.get("product_id", product_id)
        product_details.status = False
        product_details.famer_id = farmer_id
        try:
            self.db.commit()
            self.db.refresh(product_details)
        except Exception as db_error:
            raise f"An error occured: {db_error}"
        return product_details
