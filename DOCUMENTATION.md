# UNIFIND - Complete Project Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start Guide](#quick-start-guide)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [API Documentation](#api-documentation)
7. [Frontend Components](#frontend-components)
8. [Backend Services](#backend-services)
9. [Database Schema](#database-schema)
10. [Configuration](#configuration)
11. [Development Workflow](#development-workflow)
12. [Deployment Guide](#deployment-guide)
13. [Testing](#testing)
14. [Troubleshooting](#troubleshooting)
15. [Contributing](#contributing)

---

## Project Overview

**UNIFIND** is a modern college marketplace platform that enables students to buy, sell, and trade items safely within their campus community. Built with cutting-edge technologies, it features AI-powered matching, trust scores, condition grading, and real-time chat functionality.

### Key Features

- 🔐 Secure Firebase Authentication
- 🛍️ Smart Product Listings
- 🔍 **Advanced Search & Filtering** (real-time search, history, nested dropdowns)
- 📋 **Recently Viewed Products** (tracks last 10 items)
- 💬 **Quick Contact Buttons** (WhatsApp, Call)
- 🏷️ **Negotiable Badges** (price flexibility indicators)
- 🤖 AI-Powered Need Board
- ⭐ Trust Score System
- 💬 **Real-time Messaging** (3-second auto-refresh)
- 👤 **Public Profile Viewing** (with privacy protection)
- 🌙 **Dark Mode** (toggle with persistent preference)
- 📊 Analytics Dashboard
- 🎯 Advanced Sorting (6 options)
- 📱 Fully Responsive Design
- 🔒 Automatic Privacy Controls

### Repository

- **GitHub**: https://github.com/Shreyas-patil07/UNIFIND
- **License**: MIT
- **Version**: 2.1.0

---

## Quick Start Guide

### Prerequisites

- Node.js 18.0+
- Python 3.11+
- Firebase account
- Git

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/Shreyas-patil07/UNIFIND.git
cd UNIFIND
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Configure Environment Variables**

Create `.env` files in both `backend/` and `frontend/` directories (see Configuration section).

5. **Run the Application**

Terminal 1 (Backend):
```bash
cd backend
python main.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

6. **Access the Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Architecture

### High-Level Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  React Frontend │ ◄─────► │  FastAPI Backend│ ◄─────► │    Firebase     │
│  (Port 5173)    │  HTTP   │  (Port 8000)    │  SDK    │   Firestore     │
│   Vite Build    │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

### Technology Choices

- **Vite**: Lightning-fast HMR (<1s startup vs 30s+ with CRA)
- **FastAPI**: Modern async Python framework with auto-docs
- **Firebase**: Managed authentication and NoSQL database
- **Tailwind CSS**: Utility-first styling for rapid development

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| Vite | 5.1.0 | Build tool with instant HMR |
| React | 18.3.1 | UI framework |
| React Router DOM | 6.22.0 | Client-side routing |
| Tailwind CSS | 3.4.1 | Utility-first CSS |
| Axios | 1.6.7 | HTTP client |
| Firebase SDK | 10.7.1 | Authentication |
| Lucide React | 0.507.0 | Icon library |
| Leaflet | 1.9.4 | Interactive maps |
| React Leaflet | 4.2.1 | React wrapper for Leaflet |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.110.1 | Web framework |
| Uvicorn | 0.25.0 | ASGI server |
| Firebase Admin | 6.4.0 | Server-side Firebase SDK |
| Pydantic | 2.6.4 | Data validation |
| Python-dotenv | 1.0.1 | Environment management |
| Pydantic Settings | 2.2.1 | Settings management |

---

## Project Structure

```
UNIFIND/
├── backend/                        # FastAPI Backend
│   ├── routes/                     # API route modules
│   │   ├── __init__.py
│   │   ├── products.py            # Product CRUD + filters
│   │   ├── users.py               # User management
│   │   ├── chats.py               # Messaging system
│   │   └── reviews.py             # Review system
│   ├── .env                        # Environment variables
│   ├── config.py                   # Configuration management
│   ├── database.py                 # Firebase initialization
│   ├── main.py                     # FastAPI app entry point
│   ├── models.py                   # Pydantic models
│   └── requirements.txt            # Python dependencies
│
├── frontend/                       # Vite + React Frontend
│   ├── public/                     # Static assets
│   │   ├── Numero_Uno.png         # Team logo
│   │   └── UNIFIND.png            # Brand logo
│   ├── src/
│   │   ├── components/            # Reusable components
│   │   │   ├── ui/                # UI primitives
│   │   │   ├── Header.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── ProductCard.jsx
│   │   │   ├── SkeletonLoader.jsx
│   │   │   ├── FloatingBadge.jsx
│   │   │   └── NumeroUnoBadge.jsx
│   │   ├── contexts/              # React contexts
│   │   │   └── AuthContext.jsx
│   │   ├── data/
│   │   │   └── mockData.js
│   │   ├── pages/                 # Page components (13 pages)
│   │   │   ├── LandingPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── SignupPage.jsx
│   │   │   ├── OTPVerificationPage.jsx
│   │   │   ├── DashboardHome.jsx
│   │   │   ├── BuyerPage.jsx
│   │   │   ├── ListingDetailPage.jsx
│   │   │   ├── SellerPage.jsx
│   │   │   ├── PostListingPage.jsx
│   │   │   ├── NeedBoardPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── AnalyticsPage.jsx
│   │   │   └── ProfilePage.jsx
│   │   ├── services/
│   │   │   ├── api.js             # Backend API service
│   │   │   └── firebase.js        # Firebase client config
│   │   ├── utils/
│   │   │   ├── cn.js              # Class name merger
│   │   │   ├── constants.js       # App constants
│   │   │   └── recentlyViewed.js  # Recently viewed tracking
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .env                        # Environment variables
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── .gitignore
├── DOCUMENTATION.md               # This file
└── README.md                      # Project README
```

---

## API Documentation

### Base URL

- Development: `http://localhost:8000/api`
- Production: Configure via `VITE_API_URL`

### Authentication

Currently using Firebase Authentication. Backend validates Firebase tokens.

### Endpoints

#### Products API

**GET /api/products**
- Description: Get all products with optional filters
- Query Parameters:
  - `category` (optional): Filter by category
  - `min_price` (optional): Minimum price
  - `max_price` (optional): Maximum price
  - `condition` (optional): Filter by condition
  - `seller_id` (optional): Filter by seller
- Response: Array of Product objects

**POST /api/products**
- Description: Create a new product listing
- Request Body: ProductCreate object
- Response: Product object with generated ID

**GET /api/products/{product_id}**
- Description: Get specific product details
- Side Effect: Increments view count
- Response: Product object

**PUT /api/products/{product_id}**
- Description: Update product listing
- Request Body: ProductCreate object
- Response: Updated Product object

**DELETE /api/products/{product_id}**
- Description: Delete product (soft delete)
- Response: Success message

#### Users API

**GET /api/users**
- Description: Get all users (core data only)
- Response: Array of User objects

**POST /api/users**
- Description: Create new user (also creates profile automatically)
- Request Body: UserCreate object
- Response: Object with user and profile data

**GET /api/users/{user_id}**
- Description: Get user core data by ID
- Response: User object

**GET /api/users/firebase/{firebase_uid}**
- Description: Get user by Firebase UID
- Response: User object

**PUT /api/users/{user_id}**
- Description: Update user core data (name, email, college)
- Request Body: Updates object
- Response: Updated User object

#### User Profiles API

**GET /api/users/{user_id}/profile**
- Description: Get user profile (public data by default)
- Query Parameters:
  - `include_private` (optional): Include private fields (default: false)
- Response: UserProfile object

**PUT /api/users/{user_id}/profile**
- Description: Update user profile
- Request Body: Profile updates object
- Response: Updated UserProfile object

#### Transaction History API

**GET /api/users/{user_id}/transactions**
- Description: Get user's transaction history
- Query Parameters:
  - `transaction_type` (optional): Filter by "buy" or "sell"
- Response: Array of Transaction objects (newest first)

**POST /api/users/{user_id}/transactions**
- Description: Create new transaction record
- Request Body: TransactionCreate object
- Response: Transaction object

**PUT /api/transactions/{transaction_id}**
- Description: Update transaction status
- Request Body: Updates object
- Response: Updated Transaction object

#### Chats API

**POST /api/chats/messages**
- Description: Send message
- Request Body: MessageCreate object
- Side Effects: Creates chat room if needed, updates unread count
- Response: Message object with deterministic chat_room_id
- Implementation: Uses min/max logic for consistent chat_room_id generation

**GET /api/chats/{user_id}**
- Description: Get all chat rooms for user
- Query Parameters:
  - `friends_only` (optional): Filter to friends only
- Response: Array of ChatRoom objects with is_friend flag
- Performance: Optimized with friendship status caching

**GET /api/chats/room/{chat_room_id}/messages**
- Description: Get messages in chat room
- Response: Array of Message objects sorted by timestamp ASC
- Implementation: Sorted in Python to avoid Firestore index requirement
- Note: Returns all messages for client-side merge logic

**GET /api/chats/between/{user1_id}/{user2_id}**
- Description: Get or create chat room between two users
- Query Parameters:
  - `product_id` (optional): Associate chat with product
- Response: ChatRoom object with deterministic ID
- Implementation: ID format: `{min_user}_{max_user}_{product_id?}`
- Guarantees: Same users always get same chat room

**PUT /api/chats/{chat_room_id}/mark-read/{user_id}**
- Description: Mark messages as read
- Side Effects: Resets unread count, updates is_read flag
- Response: Success message
- Implementation: Batch update for performance

### Chat System Architecture

**Core Principles**:
1. Single source of truth = Backend
2. Deterministic chat_room_id generation
3. Frontend uses Map-based merge (never blindly overwrites)
4. Optimistic UI for instant feedback

**Message Flow**:
1. User sends message → Optimistic UI (temp ID)
2. Backend saves with deterministic chat_room_id
3. Backend returns message with real ID
4. Frontend replaces optimistic with real message
5. Polling merges backend data (preserves optimistic)

**Key Features**:
- ✅ No message disappearing (Map-based merge)
- ✅ No duplicates (Map deduplication by ID)
- ✅ Instant feedback (optimistic UI)
- ✅ Error recovery (failed messages removed)
- ✅ Proper ordering (sorted by timestamp)

**Implementation Details**:
- Backend: `backend/routes/chats.py` with debug logging
- Frontend: `frontend/src/pages/ChatPage.jsx` with Map-based merge
- Polling: 5 seconds for messages, 10 seconds for chat list
- State: Message status (pending/sent/delivered/read)

#### Reviews API

**POST /api/reviews**
- Description: Create review
- Request Body: ReviewCreate object
- Side Effects: Updates user rating
- Response: Review object

**GET /api/reviews/user/{user_id}**
- Description: Get reviews for user
- Response: Array of Review objects

**GET /api/reviews/product/{product_id}**
- Description: Get reviews for product
- Response: Array of Review objects

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.

---

## Frontend Components

### Pages (13 total)

1. **LandingPage** - Public homepage with features and CTA
2. **LoginPage** - User authentication
3. **SignupPage** - New user registration
4. **OTPVerificationPage** - Email/phone verification
5. **DashboardHome** - User dashboard overview
6. **BuyerPage** - Browse product listings
7. **ListingDetailPage** - Detailed product view
8. **SellerPage** - Seller dashboard
9. **PostListingPage** - Create new listing
10. **NeedBoardPage** - AI-powered matching
11. **ChatPage** - Real-time messaging
12. **AnalyticsPage** - Seller analytics
13. **ProfilePage** - User profile and trust score

### Reusable Components

- **Header** - Navigation header
- **Footer** - Footer with team branding
- **ProductCard** - Product display card
- **SkeletonLoader** - Loading placeholder
- **FloatingBadge** - Floating action badge
- **NumeroUnoBadge** - Team branding badge
- **Button** - Reusable button component

### Contexts

- **AuthContext** - Firebase authentication state management
- **ThemeContext** - Dark mode state management and persistence

### Utilities

- **cn.js** - Class name merger utility (clsx + tailwind-merge)
- **constants.js** - Application constants and configuration
- **recentlyViewed.js** - Recently viewed products tracking
  - `addToRecentlyViewed(product)` - Add product to history
  - `getRecentlyViewed()` - Retrieve viewing history
  - `clearRecentlyViewed()` - Clear all history
  - Stores up to 10 most recent items in localStorage

---

## Backend Services

### Main Application (main.py)

- FastAPI app initialization
- CORS middleware configuration
- Route registration
- Firebase initialization on startup

### Configuration (config.py)

- Environment variable management
- Firebase credentials
- CORS origins configuration

### Database (database.py)

- Firebase Admin SDK initialization
- Firestore client access
- Connection management

### Models (models.py)

Pydantic models for data validation:

- **User Models (Core Authentication)**:
  - UserBase: name, email, college
  - UserCreate: UserBase + firebase_uid
  - User: UserBase + id, firebase_uid, email_verified, created_at

- **User Profile Models (Extended Information)**:
  - UserProfileBase: branch, avatar, bio, ratings, phone, hostel_room, histories
  - UserProfileCreate: UserProfileBase + user_id
  - UserProfile: UserProfileBase + id, user_id, updated_at

- **Transaction Models**:
  - TransactionBase: user_id, product_id, transaction_type, amount, status, other_party_id
  - TransactionCreate: TransactionBase
  - Transaction: TransactionBase + id, created_at, completed_at

- **Product Models**:
  - ProductBase, ProductCreate, Product

- **Message Models**:
  - MessageBase, MessageCreate, Message

- **ChatRoom**: Complete chat room model

- **Review Models**:
  - ReviewBase, ReviewCreate, Review

---

## Database Schema

### Database Architecture

UNIFIND uses a three-collection architecture for better organization, privacy control, and scalability:

1. **users** - Core authentication data
2. **user_profiles** - Extended user information (public/private)
3. **transaction_history** - Buy/sell transaction records

### Firestore Collections

#### users (Core Authentication)
```javascript
{
  id: string,
  firebase_uid: string,
  name: string,
  email: string,
  college: string,
  email_verified: boolean,
  created_at: timestamp
}
```

#### user_profiles (Extended Information)
```javascript
{
  id: string,
  user_id: string,  // Reference to users collection
  
  // Public fields (visible to all)
  branch: string,
  avatar: string,
  cover_gradient: string,
  bio: string,
  trust_score: number (0-100),
  rating: number (0-5),
  review_count: number,
  member_since: string,
  
  // Private fields (visible only to owner)
  phone: string,
  hostel_room: string,
  branch_change_history: array,
  photo_change_history: array,
  
  updated_at: timestamp
}
```

#### transaction_history (Buy/Sell Records)
```javascript
{
  id: string,
  user_id: string,  // Reference to users collection
  product_id: string,  // Reference to products collection
  transaction_type: string,  // "buy" or "sell"
  amount: number,
  status: string,  // "pending", "completed", "cancelled"
  other_party_id: string,  // buyer_id if selling, seller_id if buying
  created_at: timestamp,
  completed_at: timestamp  // nullable
}
```

#### products
```javascript
{
  id: string,
  seller_id: string,
  title: string,
  description: string,
  price: number,
  category: string,
  condition: string,
  condition_score: number (0-100),
  location: string,
  images: array,
  specifications: object,
  views: number,
  posted_date: timestamp,
  is_active: boolean
}
```

#### chat_rooms
```javascript
{
  id: string,
  user1_id: string,
  user2_id: string,
  product_id: string,
  last_message: string,
  last_message_time: timestamp,
  unread_count_user1: number,
  unread_count_user2: number,
  created_at: timestamp
}
```

#### messages
```javascript
{
  id: string,
  text: string,
  sender_id: string,
  timestamp: timestamp,
  is_read: boolean
}
```

#### reviews
```javascript
{
  id: string,
  rating: number (1-5),
  comment: string,
  reviewer_id: string,
  reviewed_user_id: string,
  product_id: string,
  created_at: timestamp
}
```

---

## Configuration

### Backend Environment Variables (.env)

```env
# Firebase Service Account
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

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Environment Variables (.env)

```env
# Firebase Client
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id

# API
VITE_API_URL=http://localhost:8000/api
```

---

## Development Workflow

### Starting Development

1. Start backend server:
```bash
cd backend
python main.py
```

2. Start frontend dev server:
```bash
cd frontend
npm run dev
```

3. Access application at http://localhost:5173

### Development Features

- **Hot Module Replacement**: Instant updates without page refresh
- **Fast Startup**: <1 second with Vite
- **Auto-reload**: Backend reloads on code changes
- **Interactive API Docs**: Test APIs at /docs

### Code Style

- Frontend: ESLint + Prettier (configured in package.json)
- Backend: PEP 8 Python style guide
- Commits: Conventional commits format

---

## Deployment Guide

### Frontend Deployment

**Recommended: Vercel**

1. Build the project:
```bash
cd frontend
npm run build
```

2. Deploy to Vercel:
```bash
vercel deploy
```

3. Set environment variables in Vercel dashboard

**Alternative Options:**
- Netlify
- Firebase Hosting
- AWS S3 + CloudFront

### Backend Deployment

**Recommended: Railway**

1. Create Railway project
2. Connect GitHub repository
3. Set environment variables
4. Deploy automatically on push

**Alternative Options:**
- Google Cloud Run
- Heroku
- DigitalOcean App Platform

### Database

Firebase Firestore is already cloud-hosted. Configure:
- Security rules in Firebase Console
- Indexes for complex queries
- Backup settings

---

## Testing

### Frontend Testing

```bash
cd frontend
npm test
```

### Backend Testing

```bash
cd backend
pytest
```

### Manual Testing Checklist

- [ ] User registration and login
- [ ] Product listing creation with image upload
- [ ] Product browsing and filtering
- [ ] Advanced search with nested categories
- [ ] Recently viewed products tracking
- [ ] Chat functionality with real-time updates
- [ ] Review submission
- [ ] Profile updates (with rate limiting)
- [ ] Analytics dashboard
- [ ] Need Board AI search (with rate limiting)
- [ ] Dark mode toggle and persistence

### Need Board Testing
1. Login to the app
2. Navigate to Need Board page
3. Enter search query (e.g., "laptop for coding")
4. Verify results show with product images
5. Check search history appears
6. Verify rate limiting (3 searches per 12 hours)
7. Click on result to navigate to product page

### Chat Testing
1. Open chat page
2. Verify chat list loads
3. Select a chat
4. Send a message
5. Switch to another tab (polling should pause)
6. Return to tab (polling should resume with immediate refresh)
7. Verify messages marked as read when visible

---

## Troubleshooting

### Common Issues

**Frontend won't start**
- Check Node.js version (18+)
- Delete `node_modules` and reinstall
- Verify `.env` file exists

**Backend won't start**
- Check Python version (3.11+)
- Verify Firebase credentials
- Check port 8000 availability

**API connection fails**
- Verify backend is running
- Check CORS configuration
- Verify `VITE_API_URL` in frontend `.env`

**Firebase errors**
- Verify project exists in Firebase Console
- Check credentials in both `.env` files
- Ensure Firestore is enabled

### Debug Mode

Enable debug logging:

Backend:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Frontend:
```javascript
console.log('Debug info:', data)
```

---

## Contributing

### How to Contribute

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Contribution Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

### Team

- **Rijul** (Team Leader) - [@Rijuls-code](https://github.com/Rijuls-code)
- **Shreyas** - [@Shreyas-patil07](https://github.com/Shreyas-patil07)
- **Atharva** - [@Atharva6153-git](https://github.com/Atharva6153-git)
- **Himanshu** - [@Himanshu052007](https://github.com/Himanshu052007)

---

## Additional Resources

- [README](README.md)
- [GitHub Repository](https://github.com/Shreyas-patil07/UNIFIND)
- [API Documentation](http://localhost:8000/docs)

---

## License

This project is licensed under the MIT License.

---

## Recent Updates

### April 6, 2026 - Dark Mode Feature

**Complete Dark Mode System**:
- Elegant toggle switch on Profile page (top right, above profile card)
- Moon icon for Light Mode, Sun icon for Dark Mode
- Applies to all pages except landing page (`/home`)
- Saves preference to Firestore database
- Persists across sessions and devices
- Smooth animations and transitions
- Mobile responsive design

**Implementation Details**:
- Created `ThemeContext.jsx` for state management
- Added `dark_mode` boolean field to user profiles
- Enabled Tailwind dark mode with `darkMode: 'class'`
- Applied dark styles to 8 pages + Header component
- Color scheme: slate-900/800 backgrounds, slate-100/200/300 text

**Pages with Dark Mode**:
- Dashboard Home, Buyer, Seller, Profile, Chat, NeedBoard, Post Listing, Header

### April 5, 2026 - Chat & Public Profiles

**Working Chat System**:
- Fully functional real-time messaging with 3-second polling
- Auto-creates chat rooms between users
- Messages persist in Firestore
- Unread message tracking
- Product context in conversations
- Mobile responsive design
- Profile integration (click to view profiles)

**Public Profile Viewing**:
- View other users' profiles via `/profile/{userId}`
- Automatic privacy protection (hides email, phone, hostel room, etc.)
- "Send Message" button on profiles
- Profile-to-chat navigation
- Loading and error states

**API Enhancements**:
- `GET /api/chats/room/{chat_room_id}/messages` - Get messages
- `GET /api/chats/between/{user1_id}/{user2_id}` - Get/create chat room
- `GET /api/users/{user_id}/profile?include_private=false` - Public profile

### April 5, 2026 - Database Restructure

**Major Update**: Restructured database from single `users` collection to three collections:

1. **users** - Core authentication data
   - id, name, email, college, firebase_uid, email_verified, created_at

2. **user_profiles** - Extended user information
   - Public: branch, avatar, bio, trust_score, rating, review_count
   - Private: phone, hostel_room, histories

3. **transaction_history** - Buy/sell transaction records
   - user_id, product_id, transaction_type, amount, status, timestamps

**Benefits**:
- ✅ Better privacy control (public/private field separation)
- ✅ Improved performance (smaller core documents)
- ✅ Enhanced scalability (dedicated transaction history)
- ✅ Flexibility (easy to extend profile fields)

**New Features**:
- Profile management endpoints
- Transaction history tracking
- Public/private profile views
- Migration script with rollback support

**Migration**: Use `backend/migrate_database.py` to migrate existing data

---

**Last Updated**: April 6, 2026 | **Version**: 2.3.0
