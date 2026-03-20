#!/usr/bin/env python3

def orm_to_dict_product(product):
    """Convert a ProductList SQLAlchemy object to a dictionary"""
    if not product:
        return None

    return {
        "id": product.id,
        "product_id": product.product_id,
        "product_name": product.product_name,
        "product_category": product.product_category,
        "price_per_kilo": product.price_per_kilo,
        "location_address": product.location_address,
        "status": product.status,
        "farmer_id": product.farmer_id,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }
