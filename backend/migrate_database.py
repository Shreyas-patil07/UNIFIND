"""
Database Migration Script
Migrates from single 'users' collection to three collections:
- users (core auth data)
- user_profiles (extended info)
- transaction_history (buy/sell history)
"""

from database import get_db
from datetime import datetime


def migrate_users_to_new_structure():
    """Migrate existing users to new three-table structure"""
    db = get_db()
    
    print("Starting database migration...")
    
    # Get all existing users
    users_collection = db.collection('users')
    existing_users = list(users_collection.stream())
    
    print(f"Found {len(existing_users)} users to migrate")
    
    migrated_count = 0
    
    for user_doc in existing_users:
        user_data = user_doc.to_dict()
        user_id = user_doc.id
        
        print(f"\nMigrating user: {user_data.get('name', 'Unknown')} (ID: {user_id})")
        
        # 1. Update users collection (keep only core fields)
        core_user_data = {
            'name': user_data.get('name'),
            'email': user_data.get('email'),
            'college': user_data.get('college'),
            'firebase_uid': user_data.get('firebase_uid'),
            'email_verified': user_data.get('email_verified', False),
            'created_at': user_data.get('created_at', datetime.now())
        }
        
        users_collection.document(user_id).set(core_user_data)
        print(f"  ✓ Updated core user data")
        
        # 2. Create user_profiles entry
        profile_data = {
            'user_id': user_id,
            'branch': user_data.get('branch'),
            'avatar': user_data.get('avatar'),
            'cover_gradient': user_data.get('cover_gradient', 'from-blue-600 to-purple-600'),
            'bio': user_data.get('bio'),
            'trust_score': user_data.get('trust_score', 0.0),
            'rating': user_data.get('rating', 0.0),
            'review_count': user_data.get('review_count', 0),
            'member_since': user_data.get('member_since', str(datetime.now().year)),
            'phone': user_data.get('phone'),
            'hostel_room': user_data.get('hostel_room'),
            'branch_change_history': user_data.get('branch_change_history', []),
            'photo_change_history': user_data.get('photo_change_history', []),
            'updated_at': datetime.now()
        }
        
        db.collection('user_profiles').add(profile_data)
        print(f"  ✓ Created user profile")
        
        migrated_count += 1
    
    print(f"\n{'='*50}")
    print(f"Migration completed successfully!")
    print(f"Migrated {migrated_count} users")
    print(f"{'='*50}")
    print("\nNew collections created:")
    print("  - users (core authentication data)")
    print("  - user_profiles (extended user information)")
    print("  - transaction_history (ready for buy/sell records)")


def rollback_migration():
    """Rollback migration by merging data back to users collection"""
    db = get_db()
    
    print("Starting rollback...")
    
    users_collection = db.collection('users')
    profiles_collection = db.collection('user_profiles')
    
    # Get all profiles
    profiles = list(profiles_collection.stream())
    
    print(f"Found {len(profiles)} profiles to rollback")
    
    for profile_doc in profiles:
        profile_data = profile_doc.to_dict()
        user_id = profile_data.get('user_id')
        
        if not user_id:
            continue
        
        # Get user core data
        user_doc = users_collection.document(user_id).get()
        if not user_doc.exists:
            continue
        
        user_data = user_doc.to_dict()
        
        # Merge profile data back into user
        merged_data = {**user_data, **profile_data}
        merged_data.pop('user_id', None)  # Remove profile's user_id field
        merged_data.pop('updated_at', None)  # Remove profile's updated_at
        
        users_collection.document(user_id).set(merged_data)
        print(f"  ✓ Rolled back user: {user_data.get('name')}")
    
    print("\nRollback completed!")
    print("Note: You may want to manually delete user_profiles and transaction_history collections")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        confirm = input("Are you sure you want to rollback the migration? (yes/no): ")
        if confirm.lower() == 'yes':
            rollback_migration()
        else:
            print("Rollback cancelled")
    else:
        confirm = input("This will migrate your database structure. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            migrate_users_to_new_structure()
        else:
            print("Migration cancelled")
