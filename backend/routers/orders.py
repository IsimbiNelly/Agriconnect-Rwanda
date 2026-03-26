from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database.session import get_db
from backend.schema.schemas import PurchaseRequestCreate, PurchaseRequestResponse, PaymentRequest, ReceiptResponse
from backend.controllers import order_controller
from backend.utils.auth import get_current_user, require_farmer, require_buyer
from backend.model.models import User

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=PurchaseRequestResponse)
async def create_order(
    data: PurchaseRequestCreate,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db),
):
    return await order_controller.create_order_async(data, current_user, db)


@router.get("/my-orders", response_model=List[PurchaseRequestResponse])
def my_orders(
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db),
):
    return order_controller.get_my_orders(current_user, db)


@router.get("/incoming", response_model=List[PurchaseRequestResponse])
def incoming_orders(
    current_user: User = Depends(require_farmer),
    db: Session = Depends(get_db),
):
    return order_controller.get_incoming_orders(current_user, db)


@router.put("/{order_id}/accept", response_model=PurchaseRequestResponse)
async def accept_order(
    order_id: int,
    current_user: User = Depends(require_farmer),
    db: Session = Depends(get_db),
):
    return await order_controller.accept_order(order_id, current_user, db)


@router.put("/{order_id}/reject", response_model=PurchaseRequestResponse)
async def reject_order(
    order_id: int,
    current_user: User = Depends(require_farmer),
    db: Session = Depends(get_db),
):
    return await order_controller.reject_order(order_id, current_user, db)


@router.put("/{order_id}/pay", response_model=ReceiptResponse)
async def pay_order(
    order_id: int,
    data: PaymentRequest,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db),
):
    return await order_controller.pay_order(order_id, current_user, data, db)


@router.put("/{order_id}/complete", response_model=PurchaseRequestResponse)
async def complete_order(
    order_id: int,
    current_user: User = Depends(require_farmer),
    db: Session = Depends(get_db),
):
    return await order_controller.complete_order(order_id, current_user, db)
