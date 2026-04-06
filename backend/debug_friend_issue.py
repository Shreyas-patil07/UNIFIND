"""
Debug script to check why add friend is failing
"""
from database import init_firebase, get_db
from datetime import datetime

def check_user_exists(user_id):
    """Check if user exists in Firestore"""
    db = get_db()
    doc = db.collection('users').document(user_id).get()
    print(f"\n=== Checking User: {user_id} ===")
    print(f"Exists: {doc.exists}")
    if doc.exists:
        data = doc.to_dict()
        print(f"Name: {data.get('name')}")
        print(f"Email: {data.get('email')}")
        print(f"College: {data.get('college')}")
        print(f"Firebase UID: {data.get('firebase_uid')}")
    return doc.exists

def list_all_users():
    """List all users in Firestore"""
    db = get_db()
    print("\n=== All Users in Firestore ===")
    users = list(db.collection('users').stream())
    print(f"Total users: {len(users)}")
    for doc in users:
        data = doc.to_dict()
        print(f"  ID: {doc.id}")
        print(f"  Name: {data.get('name')}")
        print(f"  Firebase UID: {data.get('firebase_uid')}")
        print(f"  ---")

def check_friendships():
    """Check existing friendships"""
    db = get_db()
    print("\n=== All Friendships ===")
    friendships = list(db.collection('friendships').stream())
    print(f"Total friendships: {len(friendships)}")
    for doc in friendships:
        data = doc.to_dict()
        print(f"  {data.get('user_id')} -> {data.get('friend_id')} [{data.get('status')}]")

def create_test_friendship(user_id, friend_id):
    """Manually create a test friendship"""
    db = get_db()
    print(f"\n=== Creating Test Friendship ===")
    print(f"From: {user_id}")
    print(f"To: {friend_id}")
    
    friendship_data = {
        'user_id': user_id,
        'friend_id': friend_id,
        'created_at': datetime.now(),
        'status': 'pending'
    }
    
    doc_ref = db.collection('friendships').document()
    doc_ref.set(friendship_data)
    print(f"Created friendship with ID: {doc_ref.id}")

if __name__ == "__main__":
    # Initialize Firebase
    init_firebase()
    
    # Test with the user IDs from your logs
    user_id = "xroIWPYwhQQtaYBbJyO28uDidbv1"
    friend_id = "BcDemGth3helImGgSdYS2VR28dA3"
    
    # Run diagnostics
    list_all_users()
    user_exists = check_user_exists(user_id)
    friend_exists = check_user_exists(friend_id)
    check_friendships()
    
    print("\n=== Diagnosis ===")
    if not user_exists:
        print(f"❌ User {user_id} does NOT exist in Firestore")
        print("   This user might only exist in Firebase Auth, not in the users collection")
    if not friend_exists:
        print(f"❌ Friend {friend_id} does NOT exist in Firestore")
        print("   This user might only exist in Firebase Auth, not in the users collection")
    
    if user_exists and friend_exists:
        print("✅ Both users exist - friendship should work")
        print("\nTrying to create test friendship...")
        create_test_friendship(user_id, friend_id)
    else:
        print("\n💡 Solution: Ensure users are created in Firestore during signup")
        print("   Check your signup flow to make sure it calls POST /api/users")
