#!/usr/bin/env python3

from fastapi.routing import APIRouter

router = APIRouter(
    prefix="/buyers",
    tags=["buyers"]
    )

list_buyers = [
    {"id": 1, "name": "Buyer 1", "email": "buyer1@example.com"},
    {"id": 2, "name": "Buyer 2", "email": "buyer2@example.com"},
    {"id": 3, "name": "Buyer 3", "email": "buyer3@example.com"}
    ]
@router.get("/")
async def get_buyers():
    return {"buyers": list_buyers}
