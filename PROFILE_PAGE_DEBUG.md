# Profile Page Not Loading - Debug Guide

## Issue
Cannot see profile page at: `http://localhost:3000/profile/6hG7jAJLdTeuwRF4eixKIRvR7PJ2`

## Backend Status: ✅ WORKING
- User exists: Himanshu Patil
- API returns data correctly
- Profile endpoint working: `http://localhost:8000/users/6hG7jAJLdTeuwRF4eixKIRvR7PJ2/profile`

## Quick Checks

### 1. Is the Frontend Running?

Check if you see this in your terminal:
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Note:** Vite usually runs on port 5173, not 3000!

Try opening: `http://localhost:5173/profile/6hG7jAJLdTeuwRF4eixKIRvR7PJ2`

If you're using port 3000, you might be running a different server (like Create React App).

### 2. Check What's Running on Port 3000

```bash
# Windows
netstat -ano | findstr :3000

# Then check what process it is
tasklist | findstr <PID>
```

### 3. Start the Frontend Correctly

```bash
cd frontend
npm run dev
```

This should start Vite on port 5173.

### 4. Check Browser Console

1. Open the URL in your browser
2. Press F12 to open DevTools
3. Check Console tab for errors
4. Common errors:
   - "Failed to fetch" - Backend not running
   - "404 Not Found" - Wrong URL or routing issue
   - "Cannot read property of undefined" - Data loading issue

### 5. Check Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Refresh the page
4. Look for request to: `/users/6hG7jAJLdTeuwRF4eixKIRvR7PJ2/profile`
5. Check:
   - Status code (should be 200)
   - Response data (should have user info)

## Common Issues

### Issue 1: Wrong Port
**Problem:** Trying to access port 3000 but frontend is on 5173
**Solution:** Use `http://localhost:5173/profile/6hG7jAJLdTeuwRF4eixKIRvR7PJ2`

### Issue 2: Frontend Not Running
**Problem:** No server running on port 3000 or 5173
**Solution:**
```bash
cd frontend
npm install  # If first time
npm run dev
```

### Issue 3: Backend Not Running
**Problem:** Frontend loads but shows error or blank page
**Solution:**
```bash
cd backend
uvicorn main:app --reload
```

### Issue 4: Wrong API URL
**Problem:** Frontend is calling wrong backend URL
**Check:** `frontend/.env` should have:
```
VITE_API_URL=http://localhost:8000
```

### Issue 5: Routing Issue
**Problem:** React Router not configured correctly
**Check:** Open `http://localhost:5173/` first, then navigate to profile

### Issue 6: Authentication Required
**Problem:** Profile page requires login
**Solution:** Log in first, then visit the profile page

## Step-by-Step Test

1. **Start Backend:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
   Should see: `Uvicorn running on http://127.0.0.1:8000`

2. **Test Backend API:**
   Open in browser: `http://localhost:8000/users/6hG7jAJLdTeuwRF4eixKIRvR7PJ2/profile`
   Should see JSON data with user info

3. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   Should see: `Local: http://localhost:5173/`

4. **Open Frontend:**
   Go to: `http://localhost:5173/`
   Should see the landing page

5. **Navigate to Profile:**
   Go to: `http://localhost:5173/profile/6hG7jAJLdTeuwRF4eixKIRvR7PJ2`
   Should see Himanshu Patil's profile

## What You Should See

When working correctly:
- Profile page with user's name: "Himanshu Patil"
- College: "Smt. Indira Gandhi College of Engineering (SIGCE)"
- Branch: "Computer Engineering"
- Trust score, rating, etc.

## Debug Commands

### Check if ports are in use:
```bash
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :5173
netstat -ano | findstr :8000
```

### Kill process on port (if needed):
```bash
# Windows
# Find PID first with netstat, then:
taskkill /PID <PID> /F
```

### Check frontend package.json:
```bash
cd frontend
cat package.json | grep "dev"
```

Should show something like:
```json
"dev": "vite"
```

## Still Not Working?

Please provide:
1. What URL are you trying to access?
2. What do you see in the browser? (blank page, error message, etc.)
3. Screenshot of browser console (F12 → Console tab)
4. Screenshot of Network tab (F12 → Network tab)
5. Output of `npm run dev` command
6. Are you logged in? If yes, as which user?

## Quick Test

Run this in your terminal:

```bash
# Test backend
curl http://localhost:8000/users/6hG7jAJLdTeuwRF4eixKIRvR7PJ2/profile

# Should return JSON with user data
```

If this works, the backend is fine. The issue is in the frontend.
