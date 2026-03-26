"""Product controller — CRUD, ratings, notifications."""
import os, uuid
from datetime import datetime
from typing import Optional, List

import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.model.models import Product, ProductCategory, Rating, Notification, User, UserRole
from backend.schema.schemas import ProductResponse, RatingCreate, RatingResponse
from backend.services.notification_service import create_notification, push, broadcast_to_buyers

UPLOAD_DIR = "static/uploads"


# ── Rating helpers ────────────────────────────────────────────────────────────

def _rating_stats(product_id: int, db: Session):
    row = (
        db.query(func.avg(Rating.rating), func.count(Rating.id))
        .filter(Rating.product_id == product_id)
        .first()
    )
    avg = round(float(row[0]), 1) if row[0] is not None else None
    return avg, (row[1] or 0)


def enrich(product: Product, db: Session) -> ProductResponse:
    avg, cnt = _rating_stats(product.id, db)
    resp = ProductResponse.model_validate(product)
    return resp.model_copy(update={"avg_rating": avg, "rating_count": cnt})


# ── Image upload ──────────────────────────────────────────────────────────────

async def save_image(image: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext      = os.path.splitext(image.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(await image.read())
    return f"/static/uploads/{filename}"


# ── CRUD ──────────────────────────────────────────────────────────────────────

def list_products(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> List[ProductResponse]:
    q = db.query(Product).filter(Product.is_active == True)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    if category:
        q = q.filter(Product.category == category)
    if location:
        q = q.filter(Product.location.ilike(f"%{location}%"))
    if min_price is not None:
        q = q.filter(Product.price_per_kg >= min_price)
    if max_price is not None:
        q = q.filter(Product.price_per_kg <= max_price)
    return [enrich(p, db) for p in q.order_by(Product.created_at.desc()).all()]


def get_my_products(farmer_id: int, db: Session) -> List[ProductResponse]:
    products = (
        db.query(Product)
        .filter(Product.farmer_id == farmer_id)
        .order_by(Product.created_at.desc())
        .all()
    )
    return [enrich(p, db) for p in products]


def get_product(product_id: int, db: Session) -> ProductResponse:
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return enrich(p, db)


async def create_product(
    farmer: User,
    db: Session,
    name: str,
    description: Optional[str],
    price_per_kg: float,
    quantity_available: float,
    category: str,
    location: str,
    image: Optional[UploadFile] = None,
) -> ProductResponse:
    image_url = await save_image(image) if image and image.filename else None

    product = Product(
        name=name,
        description=description,
        price_per_kg=price_per_kg,
        quantity_available=quantity_available,
        category=category,
        location=location,
        image_url=image_url,
        farmer_id=farmer.id,
    )
    db.add(product)

    # Persist notification for all active buyers
    buyers = db.query(User).filter(User.role == UserRole.buyer, User.is_active == True).all()
    for buyer in buyers:
        create_notification(
            db, buyer.id,
            "New Product Available!",
            f"{farmer.full_name} listed {name} at RWF {price_per_kg:,.0f}/kg from {location}.",
            "product",
        )

    db.commit()
    db.refresh(product)

    # Real-time push to all buyers
    await broadcast_to_buyers(db, {
        "type": "product",
        "title": "New Product Available!",
        "body": f"{name} by {farmer.full_name} — RWF {price_per_kg:,.0f}/kg",
        "product_id": product.id,
    })

    return enrich(product, db)


async def update_product(
    product_id: int,
    farmer: User,
    db: Session,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price_per_kg: Optional[float] = None,
    quantity_available: Optional[float] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    is_active: Optional[str] = None,
    image: Optional[UploadFile] = None,
) -> ProductResponse:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    if product.farmer_id != farmer.id:
        raise HTTPException(403, "Not authorized")

    if name               is not None: product.name               = name
    if description        is not None: product.description        = description
    if price_per_kg       is not None: product.price_per_kg       = price_per_kg
    if quantity_available is not None: product.quantity_available = quantity_available
    if category           is not None: product.category           = category
    if location           is not None: product.location           = location
    if is_active          is not None: product.is_active          = is_active.lower() == "true"
    if image and image.filename:       product.image_url          = await save_image(image)

    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return enrich(product, db)


def delete_product(product_id: int, farmer: User, db: Session) -> dict:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    if product.farmer_id != farmer.id:
        raise HTTPException(403, "Not authorized")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}


# ── Ratings ───────────────────────────────────────────────────────────────────

async def rate_product(product_id: int, buyer: User, data: RatingCreate, db: Session) -> RatingResponse:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    existing = db.query(Rating).filter(
        Rating.buyer_id == buyer.id,
        Rating.product_id == product_id,
    ).first()

    if existing:
        existing.rating = data.rating
        existing.review = data.review
        db.commit()
        db.refresh(existing)
        rating = existing
    else:
        rating = Rating(buyer_id=buyer.id, product_id=product_id, rating=data.rating, review=data.review)
        db.add(rating)
        db.commit()
        db.refresh(rating)

    avg, cnt = _rating_stats(product_id, db)
    await push(product.farmer_id, {
        "type": "rating",
        "title": f"New rating on {product.name}",
        "body": f"{buyer.full_name} rated {product.name} {data.rating}/10"
                + (f': "{data.review}"' if data.review else ""),
        "product_id": product_id,
        "rating": data.rating,
        "avg_rating": avg,
        "rating_count": cnt,
    })
    return rating


def get_ratings(product_id: int, db: Session) -> List[RatingResponse]:
    return (
        db.query(Rating)
        .filter(Rating.product_id == product_id)
        .order_by(Rating.created_at.desc())
        .all()
    )


# ── Notifications ─────────────────────────────────────────────────────────────

def list_notifications(user_id: int, db: Session):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )


def mark_notifications_read(user_id: int, db: Session) -> dict:
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"ok": True}
