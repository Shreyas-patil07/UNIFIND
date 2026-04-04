from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from database import get_db
from models import Message, MessageCreate, ChatRoom

router = APIRouter()


@router.post("/chats/messages", response_model=Message)
async def send_message(message: MessageCreate):
    """Send a message and create/update chat room"""
    db = get_db()
    
    # Create message
    message_data = message.model_dump()
    message_data['timestamp'] = datetime.now()
    message_data['is_read'] = False
    
    # Find or create chat room
    chat_room_id = f"{min(message.sender_id, message.receiver_id)}_{max(message.sender_id, message.receiver_id)}"
    if message.product_id:
        chat_room_id += f"_{message.product_id}"
    
    chat_room_ref = db.collection('chat_rooms').document(chat_room_id)
    chat_room = chat_room_ref.get()
    
    if not chat_room.exists:
        # Create new chat room
        chat_room_data = {
            'user1_id': min(message.sender_id, message.receiver_id),
            'user2_id': max(message.sender_id, message.receiver_id),
            'product_id': message.product_id,
            'last_message': message.text,
            'last_message_time': datetime.now(),
            'unread_count_user1': 1 if message.receiver_id == min(message.sender_id, message.receiver_id) else 0,
            'unread_count_user2': 1 if message.receiver_id == max(message.sender_id, message.receiver_id) else 0,
            'created_at': datetime.now()
        }
        chat_room_ref.set(chat_room_data)
    else:
        # Update existing chat room
        chat_data = chat_room.to_dict()
        unread_field = 'unread_count_user1' if message.receiver_id == chat_data['user1_id'] else 'unread_count_user2'
        chat_room_ref.update({
            'last_message': message.text,
            'last_message_time': datetime.now(),
            unread_field: chat_data.get(unread_field, 0) + 1
        })
    
    # Add message to messages collection
    message_ref = db.collection('messages').document()
    message_ref.set(message_data)
    
    message_data['id'] = message_ref.id
    return message_data


@router.get("/chats/{user_id}", response_model=List[ChatRoom])
async def get_user_chats(user_id: str):
    """Get all chat rooms for a user"""
    db = get_db()
    
    # Get chat rooms where user is either user1 or user2
    chats1 = db.collection('chat_rooms').where('user1_id', '==', user_id).stream()
    chats2 = db.collection('chat_rooms').where('user2_id', '==', user_id).stream()
    
    chat_rooms = []
    for doc in list(chats1) + list(chats2):
        chat_data = doc.to_dict()
        chat_data['id'] = doc.id
        chat_rooms.append(chat_data)
    
    # Sort by last message time
    chat_rooms.sort(key=lambda x: x.get('last_message_time', datetime.min), reverse=True)
    
    return chat_rooms


@router.get("/chats/{chat_room_id}/messages", response_model=List[Message])
async def get_chat_messages(chat_room_id: str):
    """Get all messages in a chat room"""
    db = get_db()
    
    messages = []
    for doc in db.collection('messages').where('chat_room_id', '==', chat_room_id).order_by('timestamp').stream():
        message_data = doc.to_dict()
        message_data['id'] = doc.id
        messages.append(message_data)
    
    return messages


@router.put("/chats/{chat_room_id}/mark-read/{user_id}")
async def mark_messages_read(chat_room_id: str, user_id: str):
    """Mark all messages in a chat room as read for a user"""
    db = get_db()
    
    chat_room_ref = db.collection('chat_rooms').document(chat_room_id)
    chat_room = chat_room_ref.get()
    
    if not chat_room.exists:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    chat_data = chat_room.to_dict()
    unread_field = 'unread_count_user1' if user_id == chat_data['user1_id'] else 'unread_count_user2'
    
    chat_room_ref.update({unread_field: 0})
    
    return {"message": "Messages marked as read"}
