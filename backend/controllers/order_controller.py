"""Order controller — purchase requests and transaction simulation."""
import uuid
from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.model.models import PurchaseRequest, Product, User, UserRole, OrderStatus
from backend.schema.schemas import PurchaseRequestCreate, PurchaseRequestResponse, PaymentRequest, ReceiptResponse
from backend.services.notification_service import create_notification, push


def _next_business_day(base: datetime, days: int) -> datetime:
    """Return base + 'days' business days (skip Sat/Sun)."""
    result = base
    added = 0
    while added < days:
        result += timedelta(days=1)
        if result.weekday() < 5:   # Mon=0 … Fri=4
            added += 1
    return result


def create_order(data: PurchaseRequestCreate, buyer: User, db: Session) -> PurchaseRequestResponse:
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product or not product.is_active:
        raise HTTPException(404, "Product not found or inactive")
    if data.quantity <= 0 or data.quantity > product.quantity_available:
        raise HTTPException(400, f"Requested quantity exceeds available stock ({product.quantity_available} kg)")

    total = round(data.quantity * product.price_per_kg, 2)
    order = PurchaseRequest(
        buyer_id=buyer.id,
        farmer_id=product.farmer_id,
        product_id=product.id,
        quantity=data.quantity,
        total_price=total,
        note=data.note,
    )
    db.add(order)
    create_notification(
        db, product.farmer_id,
        "New Purchase Request",
        f"{buyer.full_name} wants {data.quantity} kg of {product.name}.",
        "order",
    )
    db.commit()
    db.refresh(order)
    return order


async def create_order_async(data: PurchaseRequestCreate, buyer: User, db: Session) -> PurchaseRequestResponse:
    order = create_order(data, buyer, db)
    await push(order.farmer_id, {
        "type": "order",
        "title": "New Purchase Request",
        "body": f"{buyer.full_name} wants {order.quantity} kg of {order.product.name}.",
    })
    return order


def get_my_orders(buyer: User, db: Session) -> List[PurchaseRequestResponse]:
    return (
        db.query(PurchaseRequest)
        .filter(PurchaseRequest.buyer_id == buyer.id)
        .order_by(PurchaseRequest.created_at.desc())
        .all()
    )


def get_incoming_orders(farmer: User, db: Session) -> List[PurchaseRequestResponse]:
    return (
        db.query(PurchaseRequest)
        .filter(PurchaseRequest.farmer_id == farmer.id)
        .order_by(PurchaseRequest.created_at.desc())
        .all()
    )


def _get_farmer_order(order_id: int, farmer: User, db: Session) -> PurchaseRequest:
    order = db.query(PurchaseRequest).filter(PurchaseRequest.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    if order.farmer_id != farmer.id:
        raise HTTPException(403, "Not authorized")
    return order


async def accept_order(order_id: int, farmer: User, db: Session) -> PurchaseRequestResponse:
    order = _get_farmer_order(order_id, farmer, db)
    if order.status != OrderStatus.pending:
        raise HTTPException(400, f"Order is already {order.status.value}")

    order.status     = OrderStatus.accepted
    order.updated_at = datetime.utcnow()
    create_notification(
        db, order.buyer_id,
        "Order Accepted!",
        f"{farmer.full_name} accepted your request for {order.quantity} kg of {order.product.name}.",
        "order",
    )
    db.commit()
    db.refresh(order)

    await push(order.buyer_id, {
        "type": "order",
        "title": "Order Accepted!",
        "body": f"Your request for {order.quantity} kg of {order.product.name} was accepted.",
    })
    return order


async def reject_order(order_id: int, farmer: User, db: Session) -> PurchaseRequestResponse:
    order = _get_farmer_order(order_id, farmer, db)
    if order.status not in (OrderStatus.pending, OrderStatus.accepted):
        raise HTTPException(400, f"Cannot reject a {order.status.value} order")

    order.status     = OrderStatus.rejected
    order.updated_at = datetime.utcnow()
    create_notification(
        db, order.buyer_id,
        "Order Rejected",
        f"Your request for {order.quantity} kg of {order.product.name} was not accepted.",
        "order",
    )
    db.commit()
    db.refresh(order)

    await push(order.buyer_id, {
        "type": "order",
        "title": "Order Rejected",
        "body": f"Your request for {order.quantity} kg of {order.product.name} was rejected.",
    })
    return order


async def pay_order(order_id: int, buyer: User, data: PaymentRequest, db: Session) -> ReceiptResponse:
    order = db.query(PurchaseRequest).filter(PurchaseRequest.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    if order.buyer_id != buyer.id:
        raise HTTPException(403, "Not authorized")
    if order.status != OrderStatus.accepted:
        raise HTTPException(400, "Order must be accepted before payment")

    # Simulate Momo payment
    receipt_id    = f"REC-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"
    now           = datetime.utcnow()
    delivery      = _next_business_day(now, 4)   # ~4 business days out
    delivery_str  = delivery.strftime("%A, %d %B %Y — 8:00 AM to 5:00 PM")

    order.status           = OrderStatus.paid
    order.payment_ref      = receipt_id
    order.payment_phone    = data.phone
    order.payment_name     = data.name
    order.payment_provider = data.provider
    order.paid_at          = now
    order.delivery_date    = delivery_str
    order.updated_at       = now

    receipt_body = (
        f"Receipt {receipt_id} | {order.product.name} × {order.quantity} kg | "
        f"RWF {order.total_price:,.0f} | via {data.provider} ({data.phone}) | "
        f"Delivery: {delivery_str}"
    )
    create_notification(db, order.buyer_id,  f"Payment Confirmed — {receipt_id}", receipt_body, "transaction")
    create_notification(db, order.farmer_id, f"Payment Received — {receipt_id}",  receipt_body, "transaction")
    db.commit()
    db.refresh(order)

    receipt = ReceiptResponse(
        receipt_id=receipt_id,
        order_id=order.id,
        product_name=order.product.name,
        quantity=order.quantity,
        price_per_kg=order.product.price_per_kg,
        total=order.total_price,
        payment_provider=data.provider,
        payment_phone=data.phone,
        payment_name=data.name,
        paid_at=now.strftime("%d %B %Y, %H:%M UTC"),
        delivery_date=delivery_str,
        buyer_name=buyer.full_name,
        farmer_name=order.farmer.full_name,
    )

    await push(order.buyer_id, {
        "type": "transaction",
        "title": f"Payment Confirmed — {receipt_id}",
        "body": f"RWF {order.total_price:,.0f} paid via {data.provider}. Delivery: {delivery_str}",
    })
    await push(order.farmer_id, {
        "type": "transaction",
        "title": f"Payment Received — {receipt_id}",
        "body": f"Buyer paid RWF {order.total_price:,.0f} via {data.provider}. Delivery due: {delivery_str}",
    })
    return receipt


async def complete_order(order_id: int, farmer: User, db: Session) -> PurchaseRequestResponse:
    order = _get_farmer_order(order_id, farmer, db)
    if order.status != OrderStatus.paid:
        raise HTTPException(400, "Order must be paid before completing")

    order.status     = OrderStatus.completed
    order.updated_at = datetime.utcnow()

    product = order.product
    product.quantity_available = max(0.0, product.quantity_available - order.quantity)
    if product.quantity_available == 0:
        product.is_active = False

    create_notification(
        db, order.buyer_id,
        "Order Delivered!",
        f"Your {order.quantity} kg of {product.name} has been marked as delivered. Thank you!",
        "transaction",
    )
    create_notification(
        db, order.farmer_id,
        "Order Fulfilled!",
        f"Delivery of {order.quantity} kg of {product.name} to {order.buyer.full_name} complete.",
        "transaction",
    )
    db.commit()
    db.refresh(order)

    await push(order.buyer_id, {
        "type": "transaction",
        "title": "Order Delivered!",
        "body": f"Your {order.quantity} kg of {product.name} has been delivered.",
    })
    await push(order.farmer_id, {
        "type": "transaction",
        "title": "Order Fulfilled!",
        "body": f"Delivery of {order.quantity} kg of {product.name} complete.",
    })
    return order
