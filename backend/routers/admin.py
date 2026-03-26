from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.database.session import get_db
from backend.schema.schemas import AdminUserResponse, PlatformStats, ProductResponse, PurchaseRequestResponse
from backend.controllers import admin_controller
from backend.controllers.product_controller import enrich
from backend.utils.auth import require_admin
from backend.model.models import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats", response_model=PlatformStats)
def platform_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_controller.get_platform_stats(db)


@router.get("/users", response_model=List[AdminUserResponse])
def list_users(
    role:      Optional[str]  = Query(None),
    search:    Optional[str]  = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_controller.list_users(db, role=role, search=search, is_active=is_active)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_controller.get_user(user_id, db)


@router.put("/users/{user_id}/activate", response_model=AdminUserResponse)
async def activate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return await admin_controller.set_user_active(user_id, True, current_user, db)


@router.put("/users/{user_id}/deactivate", response_model=AdminUserResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return await admin_controller.set_user_active(user_id, False, current_user, db)


@router.get("/products", response_model=List[ProductResponse])
def list_all_products(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    products = admin_controller.list_all_products(db)
    return [enrich(p, db) for p in products]


@router.get("/orders", response_model=List[PurchaseRequestResponse])
def list_all_orders(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_controller.list_all_orders(db)
