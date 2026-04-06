"""
Script to verify and fix user data in Firestore
This will help diagnose and fix the friend request issues
"""
from database import init_firebase, get_db
from datetime import datetime
import sys

def list_all_users():
    """List all users in Firestore"""
    db = get_db()
    print("\n" + "="*60)
    print("ALL USERS IN FIRESTORE")
    print("="*60)
    
    users = list(db.collection('users').stream())
    
    if not users:
        print("❌ NO USERS FOUND IN FIRESTORE!")
        print("\nThis means:")
        print("1. Users are not being created during signup")
        print("2. Or they're being created in a different collection")
        print("3. Or Firebase connection is not working")
        return []
    
    print(f"\n✅ Found {len(users)} users:\n")
    
    user_list = []
    for doc in users:
        data = doc.to_dict()
        user_list.append({
            'id': doc.id,
            'data': data
        })
        print(f"📋 User ID: {doc.id}")
        print(f"   Name: {data.get('name', 'N/A')}")
        print(f"   Email: {data.get('email', 'N/A')}")
        print(f"   College: {data.get('college', 'N/A')}")
        print(f"   Firebase UID: {data.get('firebase_uid', 'N/A')}")
        print(f"   Created: {data.get('created_at', 'N/A')}")
        print()
    
    return user_list

def check_specific_users(user_ids):
    """Check if specific users exist"""
    db = get_db()
    print("\n" + "="*60)
    print("CHECKING SPECIFIC USERS FROM LOGS")
    print("="*60)
    
    for user_id in user_ids:
        print(f"\n🔍 Checking: {user_id}")
        doc = db.collection('users').document(user_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            print(f"   ✅ EXISTS")
            print(f"   Name: {data.get('name', 'N/A')}")
            print(f"   Email: {data.get('email', 'N/A')}")
        else:
            print(f"   ❌ DOES NOT EXIST")
            print(f"   This is why friend requests are failing!")

def check_friendships():
    """Check all friendships"""
    db = get_db()
    print("\n" + "="*60)
    print("ALL FRIENDSHIPS")
    print("="*60)
    
    friendships = list(db.collection('friendships').stream())
    
    if not friendships:
        print("No friendships found")
        return
    
    print(f"\nFound {len(friendships)} friendships:\n")
    
    for doc in friendships:
        data = doc.to_dict()
        print(f"  {data.get('user_id')} → {data.get('friend_id')}")
        print(f"  Status: {data.get('status')}")
        print(f"  Created: {data.get('created_at')}")
        print()

def create_test_user(user_id, name, email):
    """Create a test user for debugging"""
    db = get_db()
    print(f"\n🔧 Creating test user: {user_id}")
    
    user_data = {
        'name': name,
        'email': email,
        'college': 'Smt. Indira Gandhi College of Engineering (SIGCE)',
        'branch': 'Computer Engineering',
        'year_of_admission': '2024',
        'trust_score': 0,
        'rating': 0.0,
        'review_count': 0,
        'member_since': '2024',
        'avatar': None,
        'email_verified': False,
        'dark_mode': False,
        'created_at': datetime.now().isoformat()
    }
    
    db.collection('users').document(user_id).set(user_data)
    print(f"   ✅ Created user: {name}")

def main():
    print("\n🔍 UNIFIND - User & Friendship Diagnostic Tool")
    print("="*60)
    
    # Initialize Firebase
    try:
        init_firebase()
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        sys.exit(1)
    
    # List all users
    users = list_all_users()
    
    # Check specific users from logs
    test_user_ids = [
        "xroIWPYwhQQtaYBbJyO28uDidbv1",
        "BcDemGth3helImGgSdYS2VR28dA3"
    ]
    check_specific_users(test_user_ids)
    
    # Check friendships
    check_friendships()
    
    # Provide recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if not users:
        print("\n❌ CRITICAL: No users found in Firestore!")
        print("\n📝 Action items:")
        print("1. Check if Firebase credentials are correct")
        print("2. Verify users are being created during signup")
        print("3. Check if frontend is writing to correct Firestore project")
        print("\n💡 To create test users, run:")
        print("   python verify_and_fix_users.py --create-test-users")
    else:
        print("\n✅ Users exist in Firestore")
        
        # Check if the specific users from logs exist
        db = get_db()
        missing_users = []
        for user_id in test_user_ids:
            if not db.collection('users').document(user_id).get().exists:
                missing_users.append(user_id)
        
        if missing_users:
            print(f"\n⚠️  Users from logs are missing: {len(missing_users)}")
            print("\n📝 Possible causes:")
            print("1. Frontend and backend are using different Firebase projects")
            print("2. Users were deleted")
            print("3. User IDs in logs are from Firebase Auth but not synced to Firestore")
            print("\n💡 Solution:")
            print("   Ensure AuthContext.signup() is being called and completing successfully")
        else:
            print("\n✅ All users from logs exist!")
            print("   Friend requests should work now.")
    
    # Check for --create-test-users flag
    if len(sys.argv) > 1 and sys.argv[1] == '--create-test-users':
        print("\n" + "="*60)
        print("CREATING TEST USERS")
        print("="*60)
        create_test_user(
            "xroIWPYwhQQtaYBbJyO28uDidbv1",
            "Test User 1",
            "test1@sigce.edu.in"
        )
        create_test_user(
            "BcDemGth3helImGgSdYS2VR28dA3",
            "Test User 2",
            "test2@sigce.edu.in"
        )
        print("\n✅ Test users created! Try adding friends now.")

if __name__ == "__main__":
    main()
