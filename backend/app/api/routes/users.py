"""
User routes - user management and friend operations.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_user_service
from app.schemas.user import UserCreate, UserProfileUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    """Create a new user with profile."""
    try:
        result = await user_service.register_user(user_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/search/{query}")
async def search_users(query: str, user_service: UserService = Depends(get_user_service)):
    """Search users by name."""
    if not query or len(query) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters",
        )

    users = await user_service.search_users(query, limit=20)
    return users


@router.get("/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    include_private: bool = False,
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_current_user),
):
    """Get user profile with appropriate privacy settings."""
    # Only allow private fields if requesting own profile
    if include_private and user_id != current_user:
        include_private = False

    profile = await user_service.get_user_profile(user_id, requesting_user_id=current_user)

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return profile


@router.put("/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    updates: UserProfileUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_current_user),
):
    """Update user profile."""
    # Verify user can only update their own profile
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update another user's profile"
        )

    updates_dict = updates.model_dump(exclude_unset=True)

    profile = await user_service.update_profile(user_id, updates_dict)

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    return profile


# ============= FRIEND MANAGEMENT ROUTES =============


@router.get("/{user_id}/friends/requests/pending")
async def get_pending_friend_requests(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_current_user),
):
    """Get pending friend requests for a user."""
    # Verify user can only access their own requests
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's friend requests",
        )

    requests = await user_service.get_pending_friend_requests(user_id)
    return requests


@router.get("/{user_id}/friends/check/{friend_id}")
async def check_friendship(
    user_id: str,
    friend_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_current_user),
):
    """Check friendship status between two users."""
    # Verify user can only check their own friendships
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot check another user's friendships"
        )

    status_result = await user_service.check_friendship_status(user_id, friend_id)
    return {"status": status_result}


@router.get("/{user_id}/friends")
async def get_friends(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_current_user),
):
    """Get user's friends list."""
    # Verify user can only access their own friends
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access another user's friends"
        )

    friends = await user_service.get_friends(user_id)
    return friends


@router.post("/{user_id}/friends/{friend_id}")
async def add_friend(
    user_id: str,
    friend_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_current_user),
):
    """Send a friend request."""
    # Verify user can only send requests as themselves
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot send friend request as another user",
        )

    try:
        result = await user_service.send_friend_request(user_id, friend_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{user_id}/friends/{friend_id}/accept")
async def accept_friend_request(
    user_id: str,
    friend_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_current_user),
):
    """Accept a friend request."""
    # Verify user can only accept requests for themselves
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot accept friend request for another user",
        )

    success = await user_service.accept_friend_request(user_id, friend_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found"
        )

    return {"message": "Friend request accepted", "status": "success"}


@router.put("/{user_id}/friends/{friend_id}/reject")
async def reject_friend_request(
    user_id: str,
    friend_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_current_user),
):
    """Reject a friend request."""
    # Verify user can only reject requests for themselves
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot reject friend request for another user",
        )

    success = await user_service.reject_friend_request(user_id, friend_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found"
        )

    return {"message": "Friend request rejected", "status": "success"}


@router.delete("/{user_id}/friends/{friend_id}")
async def remove_friend(
    user_id: str,
    friend_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_current_user),
):
    """Remove a friend or cancel friend request."""
    # Verify user can only remove their own friends
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove friend for another user"
        )

    success = await user_service.remove_friend(user_id, friend_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found")

    return {"message": "Friend removed successfully"}
