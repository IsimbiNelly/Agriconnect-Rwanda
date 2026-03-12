#!/usr/bin/env python3

from fastapi.routing import APIRouter
from fastapi import Depends, Header, UploadFile, Form
from sqlalchemy.orm import Session
from utils.http_status_code import NotFound, BadRequest, Unauthorized
from utils.helpers import orm_to_dict_product
from services.farmers.productmanagement.product import ProductManagementService
from schemas.application_schema import ProductList
from database.session import get_db


router = APIRouter(
    prefix="/articlesProduct",
    tags=["Products List Management"]
    )

@router.get("/")
async def home():
    """home address"""
    return {
        "message": "Welcome to Articles management routers"
    }

@router.get("/all")
async def get_all(db:Session = Depends(get_db)):
    """get all products"""
    my_product = ProductManagementService(db=db)
    all_products = my_product.get_all_products()
    if not all_products:
        raise NotFound("No product found")

    return [ProductList.model_validate(orm_to_dict_product(product)) for product in all_products]

@router.get("/all/farmers/{farmer_id}")
async def get_products_farmers(farmer_id:str, db:Session = Depends(get_db)):
    """get all products per farmer"""
    my_product = ProductManagementService(db=db)
    all_products = my_product.get_products_for_farmer(farmer_id=farmer_id)
    if not all_products:
        raise NotFound("No products found for this farmer")
    return [ProductList.model_validate(orm_to_dict_product(product)) for product in all_products]

@router.get("/all/{product_id}")
async def get_product(product_id:str, db:Session = Depends(get_db)):
    """get one product"""
    my_product = ProductManagementService(db=db)
    product_for_id = my_product.get_product(product_id=product_id)
    return ProductList.model_validate(orm_to_dict_product(product_for_id))

@router.post("/create")
async def create_product(product_payload:ProductList, farmer_id:str, db:Session = Depends(get_db)):
    """create product"""
    my_product = ProductManagementService(db=db)
    return my_product.create_product(payload=my_product, farmer_id=farmer_id)

@router.put("/update")
async def update_product(product_payload:ProductList, product_id:str, farmer_id:str, db:Session = Depends(get_db)):
    """update the product"""
    my_product = ProductManagementService(db=db)
    return my_product.update_product(farmer_id=farmer_id, product_id=product_id, product_payload=product_payload)

@router.delete("/update_status")
async def update_status(product_id:str, db:Session = Depends(get_db)):
    """update status"""
    my_product = ProductManagementService(db=db)
    return my_product.delete_product(product_id=product_id)
