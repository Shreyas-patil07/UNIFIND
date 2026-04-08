# UNIFIND - Production Deployment Guide

## Overview
This guide covers deploying UNIFIND to production:
- Backend: Render (Free tier)
- Frontend: Vercel (Free tier)
- Database: Firebase Firestore (Already cloud-hosted)

## Prerequisites
- GitHub account
- Render account (https://render.com)
- Vercel account (https://vercel.com)
- Firebase project with Firestore enabled
- Gemini API key (https://makersuite.google.com/app/apikey)

---

## Part 1: Backend Deployment (Render)

### Step 1: Prepare Repository
1. Ensure all changes are committed to GitHub
2. Push to your main branch

### Step 2: Create Render Web Service
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: unifind-backend
   - **Region**: Oregon (US West)
   - **Branch**: main
   - **Root Directory**: backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### Step 3: Set Environment Variables
In Render dashboard, add these environment variables:

```
ENVIRONMENT=production

# Firebase Service Account (from Firebase Console)
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# CORS (add your Vercel domain after frontend deployment)
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Note your backend URL: `https://unifind-backend.onrender.com`

### Step 5: Verify Deployment
Visit: `https://unifind-backend.onrender.com/api/health`

Should return:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "environment": "production"
}
```

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend
1. Update `frontend/.env` with production backend URL:
```
VITE_API_URL=https://unifind-backend.onrender.com/api
```

2. Commit and push changes

### Step 2: Deploy to Vercel
1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: dist

### Step 3: Set Environment Variables
In Vercel project settings → Environment Variables, add:

```
# Firebase Client Configuration
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id

# Backend API URL
VITE_API_URL=https://unifind-backend.onrender.com/api
```

### Step 4: Deploy
1. Click "Deploy"
2. Wait for deployment (2-3 minutes)
3. Note your frontend URL: `https://your-app.vercel.app`

### Step 5: Update Backend CORS
1. Go back to Render dashboard
2. Update `CORS_ORIGINS` environment variable:
```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```
3. Redeploy backend

---

## Part 3: Post-Deployment Configuration

### Firebase Security Rules
Update Firestore security rules in Firebase Console:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection - read public, write own
    match /users/{userId} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.uid == resource.data.firebase_uid;
    }
    
    // User profiles - read public, write own
    match /user_profiles/{profileId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    
    // Products - read all, write own
    match /products/{productId} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && request.auth.uid == resource.data.seller_id;
    }
    
    // Chat rooms - read/write if participant
    match /chat_rooms/{roomId} {
      allow read, write: if request.auth != null;
    }
    
    // Messages - read/write if authenticated
    match /messages/{messageId} {
      allow read, write: if request.auth != null;
    }
    
    // Reviews - read all, write if authenticated
    match /reviews/{reviewId} {
      allow read: if true;
      allow create: if request.auth != null;
    }
    
    // Transaction history - read/write own
    match /transaction_history/{transactionId} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.user_id;
    }
  }
}
```

### Firebase Indexes
Create these composite indexes in Firebase Console → Firestore → Indexes:

1. **products**
   - category (Ascending) + posted_date (Descending)
   - seller_id (Ascending) + posted_date (Descending)

2. **messages**
   - chat_room_id (Ascending) + timestamp (Ascending)

3. **reviews**
   - reviewed_user_id (Ascending) + created_at (Descending)
   - product_id (Ascending) + created_at (Descending)

---

## Part 4: Monitoring & Maintenance

### Health Checks
- Backend health: `https://unifind-backend.onrender.com/api/health`
- Backend readiness: `https://unifind-backend.onrender.com/api/ready`

### Logs
- **Render**: Dashboard → Your Service → Logs
- **Vercel**: Dashboard → Your Project → Deployments → View Function Logs

### Performance Monitoring
1. Enable Render metrics in dashboard
2. Enable Vercel Analytics in project settings
3. Monitor Firebase usage in Firebase Console

### Common Issues

**Issue: Backend cold starts (Render free tier)**
- Solution: First request after inactivity takes 30-60s
- Workaround: Use a cron job to ping health endpoint every 10 minutes

**Issue: CORS errors**
- Solution: Verify CORS_ORIGINS includes your Vercel domain
- Check: No trailing slashes in URLs

**Issue: Firebase connection fails**
- Solution: Verify all Firebase env vars are set correctly
- Check: FIREBASE_PRIVATE_KEY has proper newlines (\n)

**Issue: Gemini API errors**
- Solution: Verify API key is valid
- Check: API quota not exceeded

**Issue: Chat messages disappearing**
- Solution: Ensure frontend is using latest ChatPage.jsx with Map-based merge
- Check: Backend logs show correct chat_room_id generation
- Verify: No ad blockers blocking Firebase API calls (ERR_BLOCKED_BY_CLIENT)

**Issue: Duplicate chat messages**
- Solution: Verify Map-based deduplication is working
- Check: Message IDs are unique from backend
- Debug: Console log message IDs to verify uniqueness

**Issue: Chat room ID mismatch**
- Solution: Backend generates deterministic ID using min/max logic
- Check: Frontend uses selectedChat.id from backend
- Verify: Both send and fetch use same chat_room_id format

---

## Part 5: Scaling Considerations

### Current Limits (Free Tier)
- Render: 512MB RAM, sleeps after 15min inactivity
- Vercel: 100GB bandwidth/month
- Firebase: 50K reads, 20K writes per day
- Gemini: Rate limited per API key

### Scaling to 1K-10K Users

**Backend (Render)**
- Upgrade to Starter plan ($7/month): No sleep, more RAM
- Add Redis for caching AI responses
- Implement request queuing for AI endpoints

**Frontend (Vercel)**
- Pro plan if bandwidth exceeds 100GB
- Enable Vercel Edge Network
- Implement client-side caching

**Database (Firebase)**
- Upgrade to Blaze plan (pay-as-you-go)
- Optimize queries with proper indexes
- Implement pagination for large collections

**AI (Gemini)**
- Implement aggressive caching
- Use batch processing for multiple queries
- Consider fallback to simpler matching algorithm

---

## Part 6: Security Checklist

- [ ] All API keys in environment variables (not in code)
- [ ] Firebase security rules configured
- [ ] CORS properly configured
- [ ] HTTPS enforced (automatic on Render/Vercel)
- [ ] Rate limiting enabled on AI endpoints
- [ ] Input validation on all endpoints
- [ ] Error messages don't expose sensitive info
- [ ] Firebase Admin SDK credentials secured

---

## Part 7: Rollback Procedure

### Backend Rollback (Render)
1. Go to Render dashboard → Your Service
2. Click "Manual Deploy" → Select previous commit
3. Deploy

### Frontend Rollback (Vercel)
1. Go to Vercel dashboard → Your Project → Deployments
2. Find previous working deployment
3. Click "..." → "Promote to Production"

---

## Support

For deployment issues:
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs
- Firebase: https://firebase.google.com/docs

For application issues:
- GitHub Issues: https://github.com/Shreyas-patil07/UNIFIND/issues
- Email: systemrecord07@gmail.com

---

## Quick Reference

### Backend URLs
- Production: `https://unifind-backend.onrender.com`
- Health: `/api/health`
- API Docs: `/docs` (disabled in production)

### Frontend URLs
- Production: `https://your-app.vercel.app`
- Preview: Auto-generated for each PR

### Key Commands
```bash
# Local development
cd backend && python main.py
cd frontend && npm run dev

# Build frontend
cd frontend && npm run build

# Test production build locally
cd frontend && npm run preview
```

---

**Last Updated**: April 6, 2026
**Version**: 2.0.0
