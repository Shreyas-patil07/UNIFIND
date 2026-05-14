"""
Chat routes - messaging and chat room operations.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_chat_service
from app.schemas.chat import MessageCreate
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("/messages", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: str = Depends(get_current_user),
):
    """Send a message and create/update chat room."""
    try:
        message = await chat_service.send_message(message_data, current_user)
        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_chats(
    user_id: str,
    friends_only: bool = False,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: str = Depends(get_current_user),
):
    """Get all chat rooms for a user, optionally filtered to friends only."""
    # Verify user can only access their own chats
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access other user's chats"
        )

    chats = await chat_service.get_user_chats(user_id, friends_only)
    return chats


@router.get("/room/{chat_room_id}/messages", response_model=List[Dict[str, Any]])
async def get_chat_messages(
    chat_room_id: str,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: str = Depends(get_current_user),
):
    """Get all messages in a chat room."""
    try:
        messages = await chat_service.get_chat_messages(chat_room_id, current_user)
        return messages
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/between/{user1_id}/{user2_id}")
async def get_or_create_chat_room(
    user1_id: str,
    user2_id: str,
    product_id: Optional[str] = None,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: str = Depends(get_current_user),
):
    """Get or create a chat room between two users."""
    try:
        chat_room = await chat_service.get_or_create_chat_room(
            user1_id, user2_id, product_id, current_user
        )
        return chat_room
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{chat_room_id}/mark-read/{user_id}")
async def mark_messages_read(
    chat_room_id: str,
    user_id: str,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: str = Depends(get_current_user),
):
    """Mark all messages in a chat room as read for a user."""
    # Verify user can only mark their own messages as read
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot mark messages as read for another user",
        )

    try:
        count = await chat_service.mark_messages_as_read(chat_room_id, user_id)
        return {"message": "Messages marked as read", "chat_room_id": chat_room_id, "count": count}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
