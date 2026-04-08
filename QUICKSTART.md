# 🚀 UNIFIND - Quick Start Guide

Get UNIFIND up and running in 5 minutes!

---

## 📋 Prerequisites

Before you begin, make sure you have:

- ✅ **Node.js** 18.0 or higher ([Download](https://nodejs.org/))
- ✅ **Python** 3.11 or higher ([Download](https://www.python.org/downloads/))
- ✅ **Git** ([Download](https://git-scm.com/downloads))
- ✅ **Firebase Account** ([Sign up](https://firebase.google.com/))

Check your versions:
```bash
node --version    # Should be 18.0+
python --version  # Should be 3.11+
git --version
```

---

## 🎯 Step 1: Clone the Repository

```bash
git clone https://github.com/Shreyas-patil07/UNIFIND.git
cd UNIFIND
```

---

## 🔥 Step 2: Firebase Setup

### 2.1 Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Name it (e.g., "unifind-yourname")
4. Disable Google Analytics (optional)
5. Click "Create project"

### 2.2 Enable Firestore Database

1. In Firebase Console, go to **Build** → **Firestore Database**
2. Click "Create database"
3. Choose "Start in test mode"
4. Select your region
5. Click "Enable"

### 2.3 Enable Authentication

1. Go to **Build** → **Authentication**
2. Click "Get started"
3. Enable **Email/Password** provider
4. Click "Save"

### 2.4 Get Firebase Credentials

**For Frontend:**
1. Go to **Project Settings** (gear icon)
2. Scroll to "Your apps" section
3. Click the web icon `</>`
4. Register your app (name: "UNIFIND Web")
5. Copy the config values

**For Backend:**
1. Go to **Project Settings** → **Service accounts**
2. Click "Generate new private key"
3. Download the JSON file
4. Keep it safe (don't commit to git!)

---

## ⚙️ Step 3: Configure Environment Variables

### 3.1 Backend Configuration

Create `backend/.env` file:

```bash
cd backend
```

Create a file named `.env` and paste:

```env
# Firebase Service Account (from downloaded JSON)
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**💡 Tip:** Copy values from the downloaded JSON file:
- `type` → `FIREBASE_TYPE`
- `project_id` → `FIREBASE_PROJECT_ID`
- `private_key_id` → `FIREBASE_PRIVATE_KEY_ID`
- `private_key` → `FIREBASE_PRIVATE_KEY`
- `client_email` → `FIREBASE_CLIENT_EMAIL`
- etc.

### 3.2 Frontend Configuration

```bash
cd ../frontend
```

Create a file named `.env` and paste:

```env
# Firebase Client Configuration (from Firebase Console)
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id

# API Configuration
VITE_API_URL=http://localhost:8000/api
```

**💡 Tip:** Use the config values from Step 2.4 (Frontend section)

---

## 🔧 Step 4: Install Dependencies

### 4.1 Backend Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4.2 Frontend Dependencies

Open a **new terminal** window:

```bash
cd frontend

# Install dependencies
npm install
```

---

## ▶️ Step 5: Run the Application

### 5.1 Start Backend Server

In the **first terminal** (with virtual environment activated):

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ Backend is running at: **http://localhost:8000**  
✅ API Docs available at: **http://localhost:8000/docs**

### 5.2 Start Frontend Server

In the **second terminal**:

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.1.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ Frontend is running at: **http://localhost:5173**

---

## 🎉 Step 6: Access the Application

Open your browser and go to:

👉 **http://localhost:5173**

You should see the UNIFIND landing page!

### Test the Application

1. Click **"Get Started"** or **"Sign Up"**
2. Create a new account with your email
3. Verify your email (check Firebase Console → Authentication)
4. Log in and explore the platform!

---

## 🔍 Verify Everything is Working

### Check Backend
- Visit: http://localhost:8000/docs
- You should see the interactive API documentation (Swagger UI)
- Try the `/api/health` endpoint

### Check Frontend
- Landing page loads correctly
- Sign up form works
- Login form works
- Navigation is responsive

### Check Firebase
- Go to Firebase Console → Authentication
- You should see your registered user
- Go to Firestore Database
- You should see `users` collection with your data

---

## 🛑 Common Issues & Solutions

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue: "Port 5173 already in use"
**Solution:**
```bash
# Kill the process or change port in vite.config.js
npm run dev -- --port 3000
```

### Issue: "Module not found" errors
**Solution:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Firebase connection failed"
**Solution:**
- Double-check all Firebase credentials in `.env` files
- Ensure Firestore is enabled in Firebase Console
- Ensure Authentication is enabled
- Check for typos in environment variables

### Issue: "CORS error" in browser console
**Solution:**
- Verify `CORS_ORIGINS` in `backend/.env` includes your frontend URL
- Restart the backend server after changing `.env`

### Issue: Python virtual environment not activating
**Solution:**
```bash
# Windows (PowerShell)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
venv\Scripts\activate
```

---

## 📱 Development Workflow

### Daily Development

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Making Changes

- **Frontend changes**: Auto-reload with Hot Module Replacement (instant!)
- **Backend changes**: Auto-reload with Uvicorn (restart on save)
- **Environment changes**: Restart both servers

---

## 🏗️ Building for Production

### Frontend Build
```bash
cd frontend
npm run build
# Output: dist/ folder
```

### Backend Production
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📚 Next Steps

### Learn More
- 📖 [Complete Documentation](DOCUMENTATION.md) - Full technical docs
- 👨‍💻 [Developer Guide](DEVELOPER_GUIDE.md) - Best practices and patterns
- 🚀 [Deployment Guide](DEPLOYMENT.md) - Deploy to production
- 📝 [Updates Log](UPDATES.md) - Latest changes and features

### Key Features to Explore
1. **AI Need Board** - Try natural language product search
2. **Chat System** - Message sellers about products
3. **Trust Scores** - Build your reputation
4. **Dark Mode** - Toggle in profile settings
5. **Analytics** - Track your listings performance

---

## 🐛 Troubleshooting

### Backend Issues

**"Module not found" errors**
```bash
cd backend
pip install -r requirements.txt
```

**"Firebase not initialized"**
- Check `.env` file exists in backend folder
- Verify all Firebase variables are set
- Ensure FIREBASE_PRIVATE_KEY has `\n` for newlines

**"Port 8000 already in use"**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**"Cannot find module" errors**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**"VITE_API_URL not defined"**
- Check `.env` file exists in frontend folder
- Ensure it starts with `VITE_`
- Restart dev server after changes

### Chat Issues

**Messages disappearing after sending**
- Ensure you're using latest code (v2.1.2+)
- Check browser console for errors
- Disable ad blockers (may block Firebase API)
- Verify backend logs show correct chat_room_id

**Duplicate messages appearing**
- Clear browser cache
- Check Map-based deduplication is working
- Verify message IDs are unique

**ERR_BLOCKED_BY_CLIENT error**
- Disable ad blocker for localhost
- Whitelist Firebase domains:
  - `*.googleapis.com`
  - `*.firebaseapp.com`
  - `*.firebasestorage.app`

### Database Issues

**"Permission denied" in Firestore**
- Go to Firebase Console → Firestore → Rules
- Ensure rules allow read/write for authenticated users
- Default test mode rules expire after 30 days

**"Index required" error**
- Firebase will show a link to create the index
- Click the link and wait for index to build (1-2 minutes)

### General Tips

1. **Check logs first** - Most issues show clear error messages
2. **Restart servers** - After environment variable changes
3. **Clear cache** - Browser cache can cause stale data issues
4. **Check versions** - Ensure Node 18+ and Python 3.11+
5. **Read error messages** - They usually tell you exactly what's wrong

### Still Having Issues?

1. Check [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed debugging
2. Review [UPDATES.md](UPDATES.md) for known issues
3. Open an issue on [GitHub](https://github.com/Shreyas-patil07/UNIFIND/issues)
4. Contact: systemrecord07@gmail.com

---

- 📖 Read the [Complete Documentation](DOCUMENTATION.md)
- 🔍 Explore the [API Documentation](http://localhost:8000/docs)
- 🎨 Check out the [Project Structure](README.md#-project-structure)
- 🤝 Learn about [Contributing](README.md#-contributing)
- 📋 Review [CHANGELOG_v2.1.0.md](CHANGELOG_v2.1.0.md) for latest features

## 📊 Documentation Summary

### All Documentation Updated (April 7, 2026)

All markdown files have been updated to reflect **UNIFIND v2.1.0** with:
- ✅ ChatPage critical fixes and performance optimizations
- ✅ Advanced search & filtering features
- ✅ Recently viewed products tracking
- ✅ Quick contact buttons (WhatsApp, Call)
- ✅ Negotiable badges
- ✅ Seller dashboard enhancements

**Documentation Files**:
- README.md - Main project overview
- QUICKSTART.md - This file (quick setup)
- DEVELOPER_GUIDE.md - Development reference
- DOCUMENTATION.md - Technical documentation
- MEGA_LOG.md - Project history
- CHANGELOG_v2.1.0.md - Version changelog
- DEPLOYMENT.md - Deployment guide
- LEGAL_COMPLIANCE.md - Legal documentation

---

## 💡 Pro Tips

1. **Use two terminals** - One for backend, one for frontend
2. **Keep Firebase Console open** - Monitor authentication and database in real-time
3. **Check browser console** - Helpful for debugging frontend issues
4. **Use API docs** - Test endpoints at http://localhost:8000/docs
5. **Hot reload is your friend** - Changes appear instantly in development

---

## 🆘 Need Help?

- 📧 Email: systemrecord07@gmail.com
- 🐛 GitHub Issues: [Report a bug](https://github.com/Shreyas-patil07/UNIFIND/issues)
- 📖 Full Documentation: [DOCUMENTATION.md](DOCUMENTATION.md)

---

## ✅ Quick Checklist

Before asking for help, verify:

- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Firebase project created
- [ ] Firestore enabled
- [ ] Authentication enabled
- [ ] Both `.env` files created and configured
- [ ] Dependencies installed (backend and frontend)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] No errors in terminal outputs
- [ ] No errors in browser console

---

## 🎉 What's New

### Latest Features (April 7, 2026)

**Enhanced Marketplace Experience (v2.1.0)**:
- **Advanced Search & Filtering**: Real-time search with history, nested category dropdowns (Maths levels, Graphics Kit items), and 6 sorting options
- **Recently Viewed Products**: Tracks last 10 viewed items with horizontal scroll section and clear history option
- **Quick Contact Buttons**: WhatsApp (with pre-filled message) and Call buttons on every product card
- **Negotiable Badges**: Green indicators showing which products have flexible pricing
- **Seller Dashboard**: Enhanced with search, filtering by category/status, and advanced sorting options
- **Performance**: Optimized with useMemo for smooth filtering even with large product lists

**Dark Mode**:
- Toggle between light and dark themes from your Profile page
- Elegant switch with Moon/Sun icons
- Preference saves automatically to your account
- Works across all pages (except landing page)
- Smooth transitions and animations

**Working Chat System**:
- Real-time messaging with 3-second auto-refresh
- Chat rooms auto-create between users
- Messages persist in Firestore
- Unread message tracking
- Product context support
- Mobile responsive

**Public Profile Viewing**:
- View any user's profile via `/profile/{userId}`
- Automatic privacy protection (hides email, phone, etc.)
- "Send Message" button to start chats
- Profile-to-chat integration

---

**Made with ❤️ by Numero Uno Team**

Happy coding! 🚀
