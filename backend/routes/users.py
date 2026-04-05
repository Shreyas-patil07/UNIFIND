from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from database import get_db
from models import (
    User, UserCreate, 
    UserProfile, UserProfileCreate, UserProfileBase,
    Transaction, TransactionCreate
)

router = APIRouter()


# ============= USER ROUTES (Core Authentication) =============

@router.get("/users", response_model=List[User])
async def get_users():
    """Get all users (core data only)"""
    db = get_db()
    users = []
    for doc in db.collection('users').stream():
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        users.append(user_data)
    return users


@router.post("/users", response_model=Dict[str, Any])
async def create_user(user: UserCreate):
    """Create a new user with profile"""
    db = get_db()
    
    # Check if user with firebase_uid already exists
    existing_users = db.collection('users').where('firebase_uid', '==', user.firebase_uid).limit(1).stream()
    if any(existing_users):
        raise HTTPException(status_code=400, detail="User with this Firebase UID already exists")
    
    # Create user (core data)
    user_data = user.model_dump()
    user_data['email_verified'] = False
    user_data['created_at'] = datetime.now()
    
    user_ref = db.collection('users').document()
    user_ref.set(user_data)
    user_id = user_ref.id
    
    # Create user profile (extended data)
    profile_data = {
        'user_id': user_id,
        'branch': None,
        'avatar': None,
        'cover_gradient': 'from-blue-600 to-purple-600',
        'bio': None,
        'trust_score': 0.0,
        'rating': 0.0,
        'review_count': 0,
        'member_since': str(datetime.now().year),
        'phone': None,
        'hostel_room': None,
        'branch_change_history': [],
        'photo_change_history': [],
        'dark_mode': False,
        'updated_at': datetime.now()
    }
    
    profile_ref = db.collection('user_profiles').document()
    profile_ref.set(profile_data)
    
    user_data['id'] = user_id
    profile_data['id'] = profile_ref.id
    
    return {
        'user': user_data,
        'profile': profile_data
    }


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get a specific user by ID (core data only)"""
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


@router.put("/users/{user_id}")
async def update_user(user_id: str, updates: Dict[str, Any]):
    """Update user core data (name, email, college)"""
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only allow updating specific fields
    allowed_fields = ['name', 'email', 'college', 'email_verified']
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if filtered_updates:
        doc_ref.update(filtered_updates)
    
    updated_doc = doc_ref.get()
    user_data = updated_doc.to_dict()
    user_data['id'] = user_id
    
    return user_data


# ============= USER PROFILE ROUTES (Extended Information) =============

@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str, include_private: bool = False):
    """Get user profile with user data (public data by default)"""
    db = get_db()
    
    # Verify user exists and get user data
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user_doc.to_dict()
    user_data['id'] = user_doc.id
    
    # Get profile (if exists)
    profiles = db.collection('user_profiles').where('user_id', '==', user_id).limit(1).stream()
    
    profile_data = None
    for doc in profiles:
        profile_data = doc.to_dict()
        profile_data['id'] = doc.id
        break
    
    # If no profile exists, create default profile data
    if not profile_data:
        profile_data = {
            'user_id': user_id,
            'branch': None,
            'avatar': None,
            'cover_gradient': 'from-blue-600 to-purple-600',
            'bio': None,
            'trust_score': 0.0,
            'rating': 0.0,
            'review_count': 0,
            'member_since': user_data.get('created_at', '').split('T')[0].split('-')[0] if user_data.get('created_at') else str(datetime.now().year),
            'phone': None,
            'hostel_room': None,
            'branch_change_history': [],
            'photo_change_history': [],
            'dark_mode': False
        }
    
    # Remove private fields if not requested
    if not include_private:
        private_fields = ['phone', 'hostel_room', 'branch_change_history', 'photo_change_history', 'dark_mode']
        for field in private_fields:
            profile_data.pop(field, None)
        # Also hide email from user data for public view
        user_data.pop('email', None)
    
    # Combine user and profile data
    return {
        **user_data,
        **profile_data,
        'user_id': user_id
    }


@router.put("/users/{user_id}/profile")
async def update_user_profile(user_id: str, updates: Dict[str, Any]):
    """Update user profile"""
    db = get_db()
    
    # Verify user exists
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get profile
    profiles = db.collection('user_profiles').where('user_id', '==', user_id).limit(1).stream()
    
    for doc in profiles:
        profile_ref = db.collection('user_profiles').document(doc.id)
        updates['updated_at'] = datetime.now()
        profile_ref.update(updates)
        
        updated_doc = profile_ref.get()
        profile_data = updated_doc.to_dict()
        profile_data['id'] = doc.id
        
        return profile_data
    
    raise HTTPException(status_code=404, detail="User profile not found")


# ============= TRANSACTION HISTORY ROUTES =============

@router.get("/users/{user_id}/transactions", response_model=List[Transaction])
async def get_user_transactions(user_id: str, transaction_type: str = None):
    """Get user's transaction history (buy/sell)"""
    db = get_db()
    
    # Verify user exists
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.collection('transaction_history').where('user_id', '==', user_id)
    
    if transaction_type in ['buy', 'sell']:
        query = query.where('transaction_type', '==', transaction_type)
    
    transactions = []
    for doc in query.order_by('created_at', direction='DESCENDING').stream():
        transaction_data = doc.to_dict()
        transaction_data['id'] = doc.id
        transactions.append(transaction_data)
    
    return transactions


@router.post("/users/{user_id}/transactions", response_model=Transaction)
async def create_transaction(user_id: str, transaction: TransactionCreate):
    """Create a new transaction record"""
    db = get_db()
    
    # Verify user exists
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    if transaction.user_id != user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    
    transaction_data = transaction.model_dump()
    transaction_data['created_at'] = datetime.now()
    transaction_data['completed_at'] = None
    
    doc_ref = db.collection('transaction_history').document()
    doc_ref.set(transaction_data)
    
    transaction_data['id'] = doc_ref.id
    return transaction_data


@router.put("/transactions/{transaction_id}")
async def update_transaction(transaction_id: str, updates: Dict[str, Any]):
    """Update transaction status"""
    db = get_db()
    doc_ref = db.collection('transaction_history').document(transaction_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if 'status' in updates and updates['status'] == 'completed':
        updates['completed_at'] = datetime.now()
    
    doc_ref.update(updates)
    
    updated_doc = doc_ref.get()
    transaction_data = updated_doc.to_dict()
    transaction_data['id'] = transaction_id
    
    return transaction_data
