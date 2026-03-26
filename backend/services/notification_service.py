"""
Notification service — creates DB notification rows and broadcasts real-time
WebSocket messages.
"""
from typing import List
from sqlalchemy.orm import Session

from backend.model.models import Notification, User, UserRole
from backend.utils.ws_manager import ws_manager


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    body: str,
    ntype: str = "info",
) -> Notification:
    """Persist a notification for a single user (does NOT commit)."""
    n = Notification(user_id=user_id, title=title, body=body, ntype=ntype)
    db.add(n)
    return n


async def push(user_id: int, data: dict) -> None:
    """Send a real-time WebSocket message to a single user."""
    await ws_manager.send(user_id, data)


async def broadcast_to_buyers(db: Session, data: dict) -> None:
    """Push a real-time message to ALL currently connected buyers."""
    buyer_ids = [
        row[0]
        for row in db.query(User.id).filter(
            User.role == UserRole.buyer,
            User.is_active == True,
        ).all()
    ]
    await ws_manager.broadcast(buyer_ids, data)
