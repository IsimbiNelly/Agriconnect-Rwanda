"""Message controller — conversations and real-time messaging."""
from typing import List

from fastapi import HTTPException
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from backend.model.models import Message, User, UserRole, Notification
from backend.schema.schemas import MessageCreate, MessageResponse, ConversationSummary, MessageSenderInfo
from backend.services.notification_service import create_notification, push


async def send_message(data: MessageCreate, sender: User, db: Session) -> MessageResponse:
    if data.receiver_id == sender.id:
        raise HTTPException(400, "Cannot message yourself")

    receiver = db.query(User).filter(User.id == data.receiver_id).first()
    if not receiver:
        raise HTTPException(404, "Recipient not found")

    msg = Message(sender_id=sender.id, receiver_id=data.receiver_id, content=data.content)
    db.add(msg)
    create_notification(
        db, data.receiver_id,
        f"Message from {sender.full_name}",
        data.content[:100],
        "message",
    )
    db.commit()
    db.refresh(msg)

    await push(data.receiver_id, {
        "type":      "message",
        "title":     f"Message from {sender.full_name}",
        "body":      data.content[:100],
        "sender_id": sender.id,
    })
    return msg


def list_conversations(user: User, db: Session) -> List[ConversationSummary]:
    uid = user.id

    sent_to       = {r[0] for r in db.query(Message.receiver_id).filter(Message.sender_id == uid).all()}
    received_from = {r[0] for r in db.query(Message.sender_id).filter(Message.receiver_id == uid).all()}
    partner_ids   = sent_to | received_from

    conversations = []
    for pid in partner_ids:
        partner = db.query(User).filter(User.id == pid).first()
        if not partner:
            continue

        last_msg = (
            db.query(Message)
            .filter(
                or_(
                    and_(Message.sender_id == uid, Message.receiver_id == pid),
                    and_(Message.sender_id == pid, Message.receiver_id == uid),
                )
            )
            .order_by(Message.created_at.desc())
            .first()
        )
        unread = (
            db.query(func.count(Message.id))
            .filter(Message.sender_id == pid, Message.receiver_id == uid, Message.is_read == False)
            .scalar()
        ) or 0

        conversations.append(ConversationSummary(
            other_user=MessageSenderInfo.model_validate(partner),
            last_message=last_msg.content if last_msg else "",
            last_at=last_msg.created_at if last_msg else partner.created_at,
            unread_count=unread,
        ))

    conversations.sort(key=lambda c: c.last_at, reverse=True)
    return conversations


def get_conversation(other_id: int, user: User, db: Session) -> List[MessageResponse]:
    uid  = user.id
    msgs = (
        db.query(Message)
        .filter(
            or_(
                and_(Message.sender_id == uid, Message.receiver_id == other_id),
                and_(Message.sender_id == other_id, Message.receiver_id == uid),
            )
        )
        .order_by(Message.created_at.asc())
        .all()
    )
    for m in msgs:
        if m.receiver_id == uid and not m.is_read:
            m.is_read = True
    db.commit()
    return msgs


def unread_count(user: User, db: Session) -> dict:
    count = (
        db.query(func.count(Message.id))
        .filter(Message.receiver_id == user.id, Message.is_read == False)
        .scalar()
    ) or 0
    return {"count": count}


def messageable_users(user: User, db: Session) -> List[User]:
    if user.role == UserRole.admin:
        return db.query(User).filter(User.id != user.id, User.is_active == True).all()
    target_role = UserRole.buyer if user.role == UserRole.farmer else UserRole.farmer
    return db.query(User).filter(User.role == target_role, User.is_active == True).all()
