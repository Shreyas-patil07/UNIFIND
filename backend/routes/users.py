from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from database import get_db
from models import User, UserCreate

router = APIRouter()


@router.get("/users", response_model=List[User])
async def get_users():
    """Get all users"""
    db = get_db()
    users = []
    for doc in db.collection('users').stream():
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        users.append(user_data)
    return users


@router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    db = get_db()
    
    # Check if user with firebase_uid already exists
    existing_users = db.collection('users').where('firebase_uid', '==', user.firebase_uid).limit(1).stream()
    if any(existing_users):
        raise HTTPException(status_code=400, detail="User with this Firebase UID already exists")
    
    user_data = user.model_dump()
    user_data['trust_score'] = 0.0
    user_data['rating'] = 0.0
    user_data['review_count'] = 0
    user_data['member_since'] = str(datetime.now().year)
    user_data['created_at'] = datetime.now()
    
    doc_ref = db.collection('users').document()
    doc_ref.set(user_data)
    
    user_data['id'] = doc_ref.id
    return user_data


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get a specific user by ID"""
    db = get_db()
    doc = db.collection('users').document(user_id).get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = doc.to_dict()
    user_data['id'] = doc.id
    return user_data


@router.get("/users/firebase/{firebase_uid}", response_model=User)
async def get_user_by_firebase_uid(firebase_uid: str):
    """Get a user by Firebase UID"""
    db = get_db()
    users = db.collection('users').where('firebase_uid', '==', firebase_uid).limit(1).stream()
    
    for doc in users:
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        return user_data
    
    raise HTTPException(status_code=404, detail="User not found")


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserCreate):
    """Update a user"""
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user.model_dump()
    doc_ref.update(user_data)
    
    # Get updated document
    updated_doc = doc_ref.get()
    user_data = updated_doc.to_dict()
    user_data['id'] = user_id
    
    return user_data
