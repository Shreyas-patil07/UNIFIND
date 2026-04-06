"""
Direct test of the add friend functionality
"""
from database import init_firebase, get_db
from datetime import datetime
import sys

def test_add_friend_logic(user_id, friend_id):
    """Test the exact logic from the add_friend endpoint"""
    db = get_db()
    
    print(f"\n{'='*60}")
    print(f"Testing: {user_id} → {friend_id}")
    print(f"{'='*60}\n")
    
    # Step 1: Check if same user
    if user_id == friend_id:
        print("❌ FAIL: Cannot add yourself as a friend")
        return False
    print("✅ Step 1: Different users")
    
    # Step 2: Verify both users exist
    user_doc = db.collection('users').document(user_id).get()
    friend_doc = db.collection('users').document(friend_id).get()
    
    print(f"✅ Step 2: User exists: {user_doc.exists}")
    print(f"✅ Step 2: Friend exists: {friend_doc.exists}")
    
    if not user_doc.exists:
        print(f"❌ FAIL: User {user_id} not found")
        return False
    
    if not friend_doc.exists:
        print(f"❌ FAIL: Friend {friend_id} not found")
        return False
    
    user_data = user_doc.to_dict()
    friend_data = friend_doc.to_dict()
    print(f"   User: {user_data.get('name')}")
    print(f"   Friend: {friend_data.get('name')}")
    
    # Step 3: Check if friendship already exists
    print("\n✅ Step 3: Checking for existing friendship...")
    existing = list(db.collection('friendships')
                   .where('user_id', '==', user_id)
                   .where('friend_id', '==', friend_id)
                   .limit(1)
                   .stream())
    
    if existing:
        friendship_data = existing[0].to_dict()
        status = friendship_data.get('status')
        print(f"   ⚠️  Friendship already exists with status: {status}")
        if status == 'pending':
            print("   ❌ FAIL: Friend request already sent")
            return False
        elif status == 'active':
            print("   ❌ FAIL: Already friends")
            return False
    else:
        print("   No existing friendship found")
    
    # Step 4: Check for reverse request
    print("\n✅ Step 4: Checking for reverse request...")
    reverse_request = list(db.collection('friendships')
                          .where('user_id', '==', friend_id)
                          .where('friend_id', '==', user_id)
                          .where('status', '==', 'pending')
                          .limit(1)
                          .stream())
    
    if reverse_request:
        print("   ⚠️  Reverse request found - would auto-accept")
        doc = reverse_request[0]
        doc.reference.update({'status': 'active', 'accepted_at': datetime.now()})
        
        # Create reciprocal friendship
        friendship_data = {
            'user_id': user_id,
            'friend_id': friend_id,
            'created_at': datetime.now(),
            'status': 'active',
            'accepted_at': datetime.now()
        }
        doc_ref = db.collection('friendships').document()
        doc_ref.set(friendship_data)
        
        print(f"   ✅ SUCCESS: Auto-accepted! Friendship ID: {doc_ref.id}")
        return True
    else:
        print("   No reverse request found")
    
    # Step 5: Create friend request
    print("\n✅ Step 5: Creating friend request...")
    friendship_data = {
        'user_id': user_id,
        'friend_id': friend_id,
        'created_at': datetime.now(),
        'status': 'pending'
    }
    
    doc_ref = db.collection('friendships').document()
    doc_ref.set(friendship_data)
    
    print(f"   ✅ SUCCESS: Friend request created! ID: {doc_ref.id}")
    print(f"   Status: pending")
    return True

def list_all_friendships():
    """List all friendships after test"""
    db = get_db()
    print(f"\n{'='*60}")
    print("ALL FRIENDSHIPS AFTER TEST")
    print(f"{'='*60}\n")
    
    friendships = list(db.collection('friendships').stream())
    
    if not friendships:
        print("No friendships found")
        return
    
    print(f"Found {len(friendships)} friendships:\n")
    
    for doc in friendships:
        data = doc.to_dict()
        
        # Get user names
        user_doc = db.collection('users').document(data.get('user_id')).get()
        friend_doc = db.collection('users').document(data.get('friend_id')).get()
        
        user_name = user_doc.to_dict().get('name') if user_doc.exists else 'Unknown'
        friend_name = friend_doc.to_dict().get('name') if friend_doc.exists else 'Unknown'
        
        print(f"📋 Friendship ID: {doc.id}")
        print(f"   From: {user_name} ({data.get('user_id')})")
        print(f"   To: {friend_name} ({data.get('friend_id')})")
        print(f"   Status: {data.get('status')}")
        print(f"   Created: {data.get('created_at')}")
        print()

def main():
    print("\n🧪 TESTING ADD FRIEND FUNCTIONALITY")
    
    # Initialize Firebase
    try:
        init_firebase()
        print("✅ Firebase initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        sys.exit(1)
    
    # Test with the user IDs from logs
    user_id = "xroIWPYwhQQtaYBbJyO28uDidbv1"  # Shreyas Patil
    friend_id = "BcDemGth3helImGgSdYS2VR28dA3"  # Rijul Singh
    
    try:
        success = test_add_friend_logic(user_id, friend_id)
        
        if success:
            print(f"\n{'='*60}")
            print("✅ TEST PASSED - Friend request should work!")
            print(f"{'='*60}")
        else:
            print(f"\n{'='*60}")
            print("❌ TEST FAILED - See errors above")
            print(f"{'='*60}")
        
        # Show all friendships
        list_all_friendships()
        
    except Exception as e:
        print(f"\n❌ ERROR during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
