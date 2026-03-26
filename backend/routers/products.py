from fastapi import APIRouter, Depends, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.database.session import get_db
from backend.schema.schemas import ProductResponse, RatingCreate, RatingResponse, NotificationResponse
from backend.controllers import product_controller
from backend.utils.auth import get_current_user, require_farmer, require_buyer
from backend.model.models import User

router = APIRouter(prefix="/api/products", tags=["products"])


# ── Notifications (must come before /{product_id}) ────────────────────────────

@router.get("/notifications/list", response_model=List[NotificationResponse])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return product_controller.list_notifications(current_user.id, db)


@router.post("/notifications/mark-read")
def mark_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return product_controller.mark_notifications_read(current_user.id, db)


# ── My products (must come before /{product_id}) ──────────────────────────────

@router.get("/my-products", response_model=List[ProductResponse])
def my_products(
    current_user: User = Depends(require_farmer),
    db: Session = Depends(get_db),
):
    return product_controller.get_my_products(current_user.id, db)


# ── Public listing ────────────────────────────────────────────────────────────

@router.get("", response_model=List[ProductResponse])
def list_products(
    search:    Optional[str]   = Query(None),
    category:  Optional[str]   = Query(None),
    location:  Optional[str]   = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    return product_controller.list_products(db, search, category, location, min_price, max_price)


# ── Single product ────────────────────────────────────────────────────────────

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_controller.get_product(product_id, db)


# ── Create ────────────────────────────────────────────────────────────────────

@router.post("", response_model=ProductResponse)
async def create_product(
    name:               str            = Form(...),
    description:        Optional[str]  = Form(None),
    price_per_kg:       float          = Form(...),
    quantity_available: float          = Form(...),
    category:           str            = Form(...),
    location:           str            = Form(...),
    image:              Optional[UploadFile] = File(None),
    current_user: User  = Depends(require_farmer),
    db: Session         = Depends(get_db),
):
    return await product_controller.create_product(
        farmer=current_user, db=db,
        name=name, description=description,
        price_per_kg=price_per_kg, quantity_available=quantity_available,
        category=category, location=location, image=image,
    )


# ── Update ────────────────────────────────────────────────────────────────────

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id:         int,
    name:               Optional[str]  = Form(None),
    description:        Optional[str]  = Form(None),
    price_per_kg:       Optional[float] = Form(None),
    quantity_available: Optional[float] = Form(None),
    category:           Optional[str]  = Form(None),
    location:           Optional[str]  = Form(None),
    is_active:          Optional[str]  = Form(None),
    image:              Optional[UploadFile] = File(None),
    current_user: User  = Depends(require_farmer),
    db: Session         = Depends(get_db),
):
    return await product_controller.update_product(
        product_id=product_id, farmer=current_user, db=db,
        name=name, description=description,
        price_per_kg=price_per_kg, quantity_available=quantity_available,
        category=category, location=location, is_active=is_active, image=image,
    )


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{product_id}")
def delete_product(
    product_id:   int,
    current_user: User    = Depends(require_farmer),
    db: Session           = Depends(get_db),
):
    return product_controller.delete_product(product_id, current_user, db)


# ── Rate ──────────────────────────────────────────────────────────────────────

@router.post("/{product_id}/rate", response_model=RatingResponse)
async def rate_product(
    product_id:   int,
    data:         RatingCreate,
    current_user: User    = Depends(require_buyer),
    db: Session           = Depends(get_db),
):
    return await product_controller.rate_product(product_id, current_user, data, db)


@router.get("/{product_id}/ratings", response_model=List[RatingResponse])
def get_ratings(product_id: int, db: Session = Depends(get_db)):
    return product_controller.get_ratings(product_id, db)
