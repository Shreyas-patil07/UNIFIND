"""
Test script to verify user endpoints and populate test data
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_user_exists(user_id):
    """Check if a user exists"""
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print(f"\n=== Check User {user_id} ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"User exists: {response.json().get('name')}")
        return True
    else:
        print(f"User not found: {response.text}")
        return False

def test_pending_requests(user_id):
    """Check pending friend requests"""
    response = requests.get(f"{BASE_URL}/users/{user_id}/friends/requests/pending")
    print(f"\n=== Pending Friend Requests for {user_id} ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        requests_data = response.json()
        print(f"Pending requests: {len(requests_data)}")
        for req in requests_data:
            print(f"  - From: {req.get('name')} ({req.get('id')})")
    else:
        print(f"Error: {response.text}")

def test_search_users(query):
    """Search for users"""
    response = requests.get(f"{BASE_URL}/users/search/{query}")
    print(f"\n=== Search Users: '{query}' ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - {user.get('name')} ({user.get('id')})")
    else:
        print(f"Error: {response.text}")

def test_add_friend(user_id, friend_id):
    """Test adding a friend"""
    response = requests.post(f"{BASE_URL}/users/{user_id}/friends/{friend_id}")
    print(f"\n=== Add Friend: {user_id} -> {friend_id} ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def list_all_users():
    """List all users in the system"""
    response = requests.get(f"{BASE_URL}/users")
    print(f"\n=== All Users ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"  - {user.get('name')} ({user.get('id')}) - {user.get('college')}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    # Test with the user ID from your logs
    test_user_id = "xroIWPYwhQQtaYBbJyO28uDidbv1"
    friend_user_id = "BcDemGth3helImGgSdYS2VR28dA3"
    
    # Run tests
    list_all_users()
    test_user_exists(test_user_id)
    test_user_exists(friend_user_id)
    test_pending_requests(test_user_id)
    test_search_users("Himanshu")
    test_search_users("test")
