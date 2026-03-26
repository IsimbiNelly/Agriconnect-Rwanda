"""Admin controller — platform oversight, user management."""
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.model.models import User, UserRole, Product, PurchaseRequest, OrderStatus
from backend.schema.schemas import AdminUserResponse, PlatformStats
from backend.services.notification_service import create_notification, push


# ── Users ─────────────────────────────────────────────────────────────────────

def list_users(
    db: Session,
    role: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> List[AdminUserResponse]:
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if search:
        q = q.filter(
            User.username.ilike(f"%{search}%") |
            User.full_name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
    return q.order_by(User.created_at.desc()).all()


def get_user(user_id: int, db: Session) -> AdminUserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


async def set_user_active(user_id: int, active: bool, admin: User, db: Session) -> AdminUserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.role == UserRole.admin:
        raise HTTPException(400, "Cannot deactivate another admin account")
    if user.id == admin.id:
        raise HTTPException(400, "Cannot deactivate your own account")

    user.is_active = active
    action = "activated" if active else "deactivated"

    create_notification(
        db, user.id,
        f"Account {action.capitalize()}",
        f"Your account has been {action} by an administrator.",
        "admin",
    )
    db.commit()
    db.refresh(user)

    await push(user.id, {
        "type":  "admin",
        "title": f"Account {action.capitalize()}",
        "body":  f"Your account has been {action} by an administrator.",
    })
    return user


# ── Platform stats ────────────────────────────────────────────────────────────

def get_platform_stats(db: Session) -> PlatformStats:
    total_users    = db.query(User).count()
    total_farmers  = db.query(User).filter(User.role == UserRole.farmer).count()
    total_buyers   = db.query(User).filter(User.role == UserRole.buyer).count()
    total_admins   = db.query(User).filter(User.role == UserRole.admin).count()
    active_users   = db.query(User).filter(User.is_active == True).count()
    inactive_users = db.query(User).filter(User.is_active == False).count()

    total_products  = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()

    total_orders     = db.query(PurchaseRequest).count()
    pending_orders   = db.query(PurchaseRequest).filter(PurchaseRequest.status == OrderStatus.pending).count()
    completed_orders = db.query(PurchaseRequest).filter(PurchaseRequest.status == OrderStatus.completed).count()

    return PlatformStats(
        total_users=total_users,
        total_farmers=total_farmers,
        total_buyers=total_buyers,
        total_admins=total_admins,
        active_users=active_users,
        inactive_users=inactive_users,
        total_products=total_products,
        active_products=active_products,
        total_orders=total_orders,
        pending_orders=pending_orders,
        completed_orders=completed_orders,
    )


# ── All products ──────────────────────────────────────────────────────────────

def list_all_products(db: Session) -> List[Product]:
    return db.query(Product).order_by(Product.created_at.desc()).all()


# ── All orders ────────────────────────────────────────────────────────────────

def list_all_orders(db: Session) -> List[PurchaseRequest]:
    return db.query(PurchaseRequest).order_by(PurchaseRequest.created_at.desc()).all()
