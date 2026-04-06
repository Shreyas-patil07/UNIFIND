# Friend Request Debugging Guide

## Summary
The backend is working correctly. The issue is likely in the frontend or with how Rijul is logged in.

## Test Results

### ✅ Backend Tests (All Passing)
1. **Database Check**: Friend request exists correctly
   - Shreyas → Rijul: `pending` status
   - Document ID: `WgQVPhoLzA3S5QhSp8Fg`

2. **check_friendship Endpoint**: Returns correct status
   - From Shreyas's perspective: `request_sent` ✅
   - From Rijul's perspective: `request_received` ✅

3. **get_pending_friend_requests Endpoint**: Returns correct data
   - Rijul should see 1 pending request from Shreyas ✅

## Troubleshooting Steps

### Step 1: Verify Backend is Running
```bash
cd backend
uvicorn main:app --reload
```

The server should be running on `http://localhost:8000`

### Step 2: Test API Endpoints Directly
```bash
cd backend
python test_api_call.py
```

This will test:
- GET `/users/{rijul_id}/friends/requests/pending` - Should return Shreyas's request
- GET `/users/{rijul_id}/friends/check/{shreyas_id}` - Should return `request_received`
- GET `/users/{shreyas_id}/friends/check/{rijul_id}` - Should return `request_sent`

### Step 3: Check Frontend Configuration

1. **Verify API Base URL** in `frontend/.env`:
   ```
   VITE_API_URL=http://localhost:8000
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

### Step 4: Browser Debugging (Most Important!)

1. **Log in as Rijul Singh**
   - Email: (Rijul's email)
   - Firebase UID should be: `BcDemGth3helImGgSdYS2VR28dA3`

2. **Open Browser DevTools** (F12)

3. **Check Console Tab** for errors:
   - Look for API call errors
   - Look for authentication errors
   - Look for CORS errors

4. **Check Network Tab**:
   - Filter by "XHR" or "Fetch"
   - Look for call to `/users/BcDemGth3helImGgSdYS2VR28dA3/friends/requests/pending`
   - Click on the request and check:
     - Status code (should be 200)
     - Response body (should contain Shreyas's request)

5. **Check Application Tab**:
   - Go to Local Storage
   - Verify the auth token is present
   - Verify the user ID matches Rijul's Firebase UID

### Step 5: Common Issues

#### Issue 1: Wrong User ID
**Problem**: Rijul is logged in but with a different Firebase UID
**Solution**: 
```bash
cd backend
python -c "from database import init_firebase, get_db; init_firebase(); db = get_db(); users = db.collection('users').where('email', '==', 'rijul@example.com').stream(); [print(f'{u.id}: {u.to_dict()}') for u in users]"
```
Replace `rijul@example.com` with Rijul's actual email.

#### Issue 2: API Not Being Called
**Problem**: Frontend is not calling the API
**Check**: 
- Open `frontend/src/components/Header.jsx`
- Look for `fetchFriendRequests()` function
- Add console.log to debug:
  ```javascript
  const fetchFriendRequests = async () => {
    console.log('Fetching friend requests for:', currentUser?.uid)
    if (!currentUser?.uid) return
    
    try {
      const requests = await getPendingFriendRequests(currentUser.uid)
      console.log('Friend requests received:', requests)
      setFriendRequests(requests)
    } catch (error) {
      console.error('Failed to fetch friend requests:', error)
    }
  }
  ```

#### Issue 3: CORS Error
**Problem**: Browser blocks API calls due to CORS
**Solution**: Check `backend/main.py` has CORS middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue 4: Authentication Token Missing
**Problem**: API calls fail with 401 Unauthorized
**Solution**: Check if Firebase auth token is being sent with requests in `frontend/src/services/api.js`

### Step 6: Manual Verification

If Rijul still can't see the request, try this:

1. **Click on "Find Users" button** in the header (top right)
2. **Click on "Notifications" tab**
3. **You should see**: Shreyas Patil's friend request with Accept/Decline buttons

If you don't see it:
- Check the browser console for errors
- Check the Network tab to see if the API call was made
- Check if `friendRequests` state is being updated

### Step 7: Force Refresh

Sometimes the frontend cache causes issues:

1. **Hard refresh**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. **Clear browser cache**: DevTools → Application → Clear Storage → Clear site data
3. **Restart frontend dev server**

## Quick Test Script

Run this to verify everything:

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Test API
cd backend
python test_api_call.py

# Terminal 3 - Frontend
cd frontend
npm run dev
```

Then:
1. Open browser to `http://localhost:5173`
2. Log in as Rijul Singh
3. Click "Find Users" button (top right)
4. Click "Notifications" tab
5. You should see Shreyas's friend request

## Expected Behavior

### For Shreyas (Sender)
- On Rijul's profile page: Should see "Request Sent" button (gray, disabled)
- In notifications: Should NOT see any request

### For Rijul (Receiver)
- On Shreyas's profile page: Should see "Accept Request" button (green)
- In notifications: Should see Shreyas's request with Accept/Decline buttons
- Red badge on "Find Users" button showing "1"

## Database State

Current friendships:
```
Document ID: WgQVPhoLzA3S5QhSp8Fg
- user_id: xroIWPYwhQQtaYBbJyO28uDidbv1 (Shreyas)
- friend_id: BcDemGth3helImGgSdYS2VR28dA3 (Rijul)
- status: pending
- created_at: 2026-04-07 01:40:19
```

## Next Steps

1. Run `python test_api_call.py` to verify backend is working
2. Log in as Rijul in the browser
3. Open DevTools and check Console + Network tabs
4. Report any errors you see

If you're still having issues, please provide:
- Browser console errors
- Network tab screenshot showing the API call
- The user ID that Rijul is logged in with (check Local Storage)
