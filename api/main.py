#!/usr/bin/env python

import uvicorn
from fastapi import FastAPI
from routers.buyers.buyers import router as buyers_router
from routers.farmers.product_management import router as farmer_product_router
app = FastAPI(
    title="AgriConnect API",
    description="API for AgriConnect platform to connect farmers with buyers and provide agricultural services.",
    )

app.include_router(buyers_router)
app.include_router(farmer_product_router)

@app.get("/")
async def home():
    """welcome function"""
    return {
        "message": "Welcome to AgriConnect platform"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=8000,
        reload=True
    )
