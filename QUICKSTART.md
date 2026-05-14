# 🚀 UNIFIND - Quick Start Guide

**Version**: 2.4.5 (May 15, 2026)

Get UNIFIND running in 5 minutes.

---

## Prerequisites

- Node.js 18.0+ ([Download](https://nodejs.org/))
- Python 3.11+ ([Download](https://www.python.org/downloads/))
- Git ([Download](https://git-scm.com/downloads))
- Firebase Account ([Sign up](https://firebase.google.com/))

Check versions:
```bash
node --version    # Should be 18.0+
python --version  # Should be 3.11+
```

---

## Step 1: Clone Repository

```bash
git clone https://github.com/Shreyas-patil07/UNIFIND.git
cd UNIFIND
```

---

## Step 2: Firebase Setup

1. Create Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable **Firestore Database** (test mode)
3. Enable **Email/Password Authentication**
4. Get credentials:
   - **Frontend**: Project Settings → Web app config
   - **Backend**: Project Settings → Service accounts → Generate private key (JSON file)
5. **Optional**: For AI-powered search, enable Google Cloud Gemini API in your Firebase project's Google Cloud console

---

## Step 2b: External Services Setup (Required for Full Features)

### Cloudinary (Product Image Storage)
1. Sign up at [Cloudinary](https://cloudinary.com/)
2. Get: Cloud Name, API Key, API Secret
3. Create unsigned upload preset for uploads

### Supabase (Profile Photo Storage)
1. Sign up at [Supabase](https://supabase.com/)
2. Create project and get Project URL and Anon Key
3. **Note**: Uses Row-Level Security (RLS) for privacy

### Gmail SMTP (Email Verification)
1. Use Google Account with 2FA enabled
2. Generate App Password: [Google Account Security](https://myaccount.google.com/apppasswords)
3. Use email and app password in `.env`

---

## Step 3: Configure Environment

**Required** environment variables are needed for basic functionality. **Optional** ones enable specific features.

### Backend `.env`
```env
# REQUIRED: Firebase Service Account (from downloaded JSON)
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com

# REQUIRED: CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# REQUIRED: Cloudinary (Product Images CDN)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
CLOUDINARY_UPLOAD_PRESET=your-unsigned-preset

# REQUIRED: Supabase (Profile Photos Storage with RLS)
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-key

# REQUIRED: Gmail SMTP (Email Verification)
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_PASSWORD=your-app-password

# OPTIONAL: Google Gemini API (enables AI-powered search)
GEMINI_API_KEY=your-gemini-api-key

# OPTIONAL: Sentry (error tracking and monitoring)
SENTRY_DSN=your-sentry-dsn
```

### Frontend `.env`
```env
# Firebase Client Config
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id

VITE_API_URL=http://localhost:8000/api
```

---

## Step 4: Install Dependencies

### Backend
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
```

### Frontend (new terminal)
```bash
cd frontend
npm install
```

**Note**: For production, use `requirements-prod.txt` (optimized dependency set).

---

## Step 5: Run Application

### Terminal 1 - Backend
```bash
cd backend

# Development mode (hot reload, auto-restart on code changes)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode (multiple workers, optimized)
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --timeout 120 \
  --keepalive 5 \
  --max-requests 1000 \
  --bind 0.0.0.0:8000
```
✅ Backend: http://localhost:8000  
✅ API Docs (Swagger): http://localhost:8000/docs  
✅ Health Check: http://localhost:8000/health

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
✅ Frontend: http://localhost:5173

---

## Step 6: Test

1. Open http://localhost:5173
2. Click "Sign Up"
3. Create account
4. Check email for verification link
5. Verify and log in

---

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Module Not Found
```bash
# Backend
pip install -r requirements.txt

# Frontend
rm -rf node_modules package-lock.json
npm install
```

### Firebase Connection Failed
- Double-check credentials in `.env` files
- Ensure Firestore and Authentication are enabled
- Verify no typos in environment variables

### CORS Error
- Verify `CORS_ORIGINS` includes frontend URL
- Restart backend after changing `.env`

### External Service Errors (Cloudinary, Supabase, Gmail)
- These services are **required** for full functionality
- If skipped, features like image uploads, profile photos, and email verification won't work
- Error messages will indicate which service is misconfigured
- Get credentials from services in Step 2b

### Slow Performance
- Deploy Firestore indexes from Firebase Console (Rules tab)
- Check backend logs for slow query warnings
- Verify indexes show "Enabled" status
- Consider optimizing Firestore queries if queries are slow

---

## Next Steps

- **Development**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Full Technical Docs**: See [MEGA_LOG.md](MEGA_LOG.md)

---

**Made with ❤️ by Numero Uno Team**
