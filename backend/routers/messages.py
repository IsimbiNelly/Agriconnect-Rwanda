from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database.session import get_db
from backend.schema.schemas import MessageCreate, MessageResponse, ConversationSummary, MessageSenderInfo
from backend.controllers import message_controller
from backend.utils.auth import get_current_user
from backend.model.models import User

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("", response_model=MessageResponse)
async def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await message_controller.send_message(data, current_user, db)


@router.get("/conversations", response_model=List[ConversationSummary])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return message_controller.list_conversations(current_user, db)


@router.get("/conversation/{other_id}", response_model=List[MessageResponse])
def get_conversation(
    other_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return message_controller.get_conversation(other_id, current_user, db)


@router.get("/unread-count")
def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return message_controller.unread_count(current_user, db)


@router.get("/users", response_model=List[MessageSenderInfo])
def messageable_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return message_controller.messageable_users(current_user, db)
