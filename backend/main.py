import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.database.session import engine
from backend.model import models                        # noqa: F401 – registers all ORM classes
from backend.model.models import Base
from backend.routers import auth, products, orders, messages, admin, ws as ws_router

# ── Create database tables ────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Static upload directory ───────────────────────────────────────────────────
os.makedirs("static/uploads", exist_ok=True)

# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(title="AgriConnect API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routers ───────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(messages.router)
app.include_router(admin.router)
app.include_router(ws_router.router)

# ── Static files ──────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── HTML page routes ──────────────────────────────────────────────────────────

@app.get("/")
def login_page():
    return FileResponse("static/index.html")


# Farmer pages
@app.get("/farmer/dashboard")
def farmer_dashboard():
    return FileResponse("static/farmer-dashboard.html")

@app.get("/farmer/products")
def farmer_products():
    return FileResponse("static/farmer-products.html")

@app.get("/farmer/add-product")
def farmer_add_product():
    return FileResponse("static/farmer-add-product.html")

@app.get("/farmer/edit-product/{product_id}")
def farmer_edit_product(product_id: int):
    return FileResponse("static/farmer-edit-product.html")

@app.get("/farmer/orders")
def farmer_orders():
    return FileResponse("static/farmer-orders.html")


# Buyer pages
@app.get("/buyer/dashboard")
def buyer_dashboard():
    return FileResponse("static/buyer-dashboard.html")

@app.get("/buyer/product/{product_id}")
def product_detail(product_id: int):
    return FileResponse("static/product-detail.html")

@app.get("/buyer/orders")
def buyer_orders():
    return FileResponse("static/buyer-orders.html")


# Shared
@app.get("/messages")
def messages_page():
    return FileResponse("static/messages.html")


# Admin pages
@app.get("/admin/dashboard")
def admin_dashboard():
    return FileResponse("static/admin-dashboard.html")

@app.get("/admin/users")
def admin_users():
    return FileResponse("static/admin-users.html")


if __name__ == "__main__":
    uvicorn.run("backend.main:app", port=8000, reload=True)
