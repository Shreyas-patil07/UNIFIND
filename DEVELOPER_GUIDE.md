# UNIFIND - Developer Guide

**Version**: 2.4.5 (May 15, 2026)

> **Setup Instructions**: See [QUICKSTART.md](QUICKSTART.md) for installation and running the application.

---

## Project Structure

```
UNIFIND/
├── backend/                    # FastAPI Backend (Repository Pattern)
│   ├── app/
│   │   ├── ai/                # AI Services (Gemini API)
│   │   │   ├── clients/       # gemini_client.py
│   │   │   ├── prompts/       # intent_extractor.py
│   │   │   ├── ranking/       # semantic_ranker.py, need_matcher.py
│   │   │   └── security/      # cost_guard, input/output validators
│   │   ├── api/               # API Layer
│   │   │   ├── dependencies/  # auth.py, database.py, services.py
│   │   │   └── routes/        # 10 API route modules
│   │   ├── core/              # Core Configuration
│   │   │   ├── config.py      # Settings management
│   │   │   └── database.py    # Firebase initialization
│   │   ├── repositories/      # Data Access Layer
│   │   │   ├── product_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── need_repository.py
│   │   │   ├── chat_repository.py
│   │   │   ├── transaction_repository.py
│   │   │   ├── review_repository.py
│   │   │   └── friendship_repository.py
│   │   ├── schemas/           # Pydantic Models
│   │   │   ├── product.py
│   │   │   ├── user.py
│   │   │   ├── need.py
│   │   │   ├── chat.py
│   │   │   └── transaction.py
│   │   └── services/          # Business Logic Layer
│   │       ├── auth_service.py
│   │       ├── product_service.py
│   │       ├── need_service.py
│   │       ├── user_service.py
│   │       ├── chat_service.py
│   │       ├── transaction_service.py
│   │       ├── review_service.py
│   │       ├── cloudinary_service.py
│   │       └── email_service.py
│   ├── main.py                # FastAPI app entry point
│   ├── requirements.txt       # Python dependencies
│   └── firebase-service-account.json
│
├── frontend/                  # React + Vite Frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components (19 files)
│   │   │   ├── Header.jsx
│   │   │   ├── ProductCard.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── SellerDemandBanner.jsx
│   │   │   ├── LoadingSkeleton.jsx
│   │   │   ├── ErrorBoundary.jsx
│   │   │   └── ui/           # Button, Modal, etc.
│   │   ├── contexts/         # React contexts
│   │   │   ├── AuthContext.jsx
│   │   │   └── ThemeContext.jsx
│   │   ├── pages/            # Page components (23 routes)
│   │   │   ├── LandingPage.jsx
│   │   │   ├── LoginPage.jsx / SignupPage.jsx
│   │   │   ├── DashboardHome.jsx
│   │   │   ├── BuyerPage.jsx / SellerPage.jsx
│   │   │   ├── ListingDetailPage.jsx
│   │   │   ├── PostListingPage.jsx / EditListingPage.jsx
│   │   │   ├── NeedBoardPage.jsx / PostNeedPage.jsx
│   │   │   ├── SellerDemandFeedPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── AnalyticsPage.jsx
│   │   │   ├── ProfilePage.jsx / EditProfilePage.jsx
│   │   │   └── Legal pages (Privacy, Terms, Community)
│   │   ├── services/         # API clients
│   │   │   ├── api.js        # Axios wrapper
│   │   │   ├── firebase.js   # Firebase SDK
│   │   │   └── imageService.js
│   │   ├── utils/            # Utilities
│   │   │   ├── cn.js         # Class name merger
│   │   │   ├── constants.js  # App constants
│   │   │   └── recentlyViewed.js
│   │   ├── App.jsx           # Main app with routing
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Dependencies
│   └── vite.config.js        # Vite config
│
└── docs/                      # Documentation (7 main files)
    ├── README.md             # Product overview
    ├── QUICKSTART.md         # Setup guide
    ├── DEVELOPER_GUIDE.md    # This file
    ├── DEPLOYMENT.md         # Production deployment
    ├── LEGAL_COMPLIANCE.md   # Legal compliance
    ├── MEGA_LOG.md           # Technical history
    └── UPDATES.md            # Changelog
```

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          UNIFIND Architecture                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND LAYER                                │
│  React 18.3.1 + Vite 5 + Tailwind CSS 3.4.1 + React Query              │
├─────────────────────────────────────────────────────────────────────────┤
│  23 Pages:                                                               │
│  • Landing, Auth (Login/Signup/Verify)                                  │
│  • Dashboard, Buyer, Seller, Listings                                   │
│  • NeedBoard (AI Search), PostNeed, SellerDemandFeed                   │
│  • Chat, Analytics, Profile, Legal                                      │
│                                                                          │
│  19 Components:                                                          │
│  • Header, ProductCard, MessageBubble, SellerDemandBanner              │
│  • LoadingSkeleton, ErrorBoundary, Modals, UI Components               │
│                                                                          │
│  State Management:                                                       │
│  • AuthContext (Firebase Auth + User Profile)                          │
│  • ThemeContext (Dark Mode)                                            │
│  • React Query (Data Fetching + Caching)                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            BACKEND LAYER                                 │
│         FastAPI 0.110.1 + Python 3.11+ + Repository Pattern            │
├─────────────────────────────────────────────────────────────────────────┤
│  API Routes (10):                                                        │
│  /api/auth          - Email verification                                │
│  /api/products      - CRUD, batch, mark sold/active                    │
│  /api/needs         - Demand→Supply engine                             │
│  /api/need-board    - AI search (rate limited)                         │
│  /api/chats         - Real-time messaging                              │
│  /api/users         - User management, friends                         │
│  /api/transactions  - Transaction history                              │
│  /api/reviews       - Reviews and ratings                              │
│  /api/uploads       - Image uploads (Cloudinary)                       │
│                                                                          │
│  Service Layer (9 services):                                            │
│  • auth_service, product_service, need_service                         │
│  • user_service, chat_service, transaction_service                     │
│  • review_service, cloudinary_service, email_service                   │
│                                                                          │
│  Repository Layer (7 repositories):                                     │
│  • product_repository, user_repository, need_repository                │
│  • chat_repository, transaction_repository, review_repository          │
│  • friendship_repository                                                │
│                                                                          │
│  AI Layer (Security Hardened):                                          │
│  • Gemini Client (async, timeout, retry)                               │
│  • Intent Extractor (structured data from NL)                          │
│  • Semantic Ranker (0-100 match scores)                                │
│  • Need Matcher (demand→supply matching)                               │
│  • Security: cost_guard, input/output validators                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
┌─────────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Firebase/Firestore│  │   Gemini AI     │  │   Cloudinary    │
│   10 Collections:   │  │   Semantic      │  │   Image CDN     │
│   • users           │  │   Matching      │  │   Product       │
│   • user_profiles   │  │   Intent        │  │   Images        │
│   • products        │  │   Extraction    │  │                 │
│   • needs           │  │   Rate Limited  │  │   + Supabase    │
│   • chat_rooms      │  │   Token Budget  │  │   Profile       │
│   • messages        │  │                 │  │   Photos        │
│   • transactions    │  └─────────────────┘  └─────────────────┘
│   • trans_history   │
│   • reviews         │  ┌─────────────────┐
│   • friendships     │  │   Gmail SMTP    │
│                     │  │   Email         │
│   Composite Indexes │  │   Verification  │
│   for Performance   │  │                 │
└─────────────────────┘  └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT LAYER                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  Frontend: Vercel (Free tier)                                           │
│  Backend:  Render (Free tier) - Gunicorn + Uvicorn workers             │
│  Database: Firebase Firestore (Cloud-hosted)                            │
│  Storage:  Cloudinary (Product images) + Supabase (Profile photos)     │
│  AI:       Google Gemini API (Pay-as-you-go)                           │
│  Email:    Gmail SMTP (Free)                                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Tech Stack
- **Frontend**: React 18.3.1 + Vite 5 + Tailwind CSS 3.4.1 + React Query
- **Backend**: FastAPI 0.110.1 + Python 3.11+ + Repository Pattern
- **Database**: Firebase Firestore (10 collections with composite indexes)
- **AI**: Google Gemini API (with security hardening)
- **Storage**: Cloudinary (product images) + Supabase (profile photos)
- **Deployment**: Vercel (frontend) + Render (backend)

### Data Flow
```
User Input → Frontend → Backend API → Service Layer → Repository → Firestore/Gemini → Response
```

### Database Collections (10 Total)
1. **users** - Core authentication data (name, email, college, firebase_uid)
2. **user_profiles** - Extended user info (branch, avatar, trust_score, rating, need_board_searches)
3. **products** - Product listings (title, price, category, condition, images, views, viewed_by)
4. **needs** - Buyer needs (raw_text, title, category, tags, matched_listings, interested_sellers)
5. **chat_rooms** - Chat metadata (participants, last_message_time, product_id)
6. **messages** - Chat messages (sender_id, content, timestamp, read_status)
7. **transactions** - Transaction records (product_id, seller_id, buyer_id, amount, status)
8. **transaction_history** - Product state changes (sold/active transitions)
9. **reviews** - User reviews (rating, comment, transaction_id, reviewer_id)
10. **friendships** - Friend connections (user_id, friend_id, status, created_at)

### API Routes (10 Total)
1. **`/api/auth`** - Email verification (send, verify, resend)
2. **`/api/products`** - Full CRUD, batch fetch, mark sold/active, interested buyers
3. **`/api/needs`** - Demand→Supply engine (create, match, fulfill, seller feed)
4. **`/api/need-board`** - AI-powered search with rate limiting (3 searches/12hrs)
5. **`/api/chats`** - Real-time messaging, chat rooms, mark as read
6. **`/api/users`** - User management, profile updates, friend system
7. **`/api/transactions`** - Transaction history, stats, product tracking
8. **`/api/reviews`** - Review creation, user ratings, stats
9. **`/api/uploads`** - Cloudinary image uploads (product/profile) with security
10. **`/api/__init__`** - Route aggregation

---

## Development Workflow

### Backend Architecture Patterns

**Repository Pattern** - Data access abstraction
```python
# backend/app/repositories/product_repository.py
class ProductRepository:
    """Handles all Firestore operations for products."""
    
    async def get_by_id(self, product_id: str) -> Optional[Dict]:
        """Fetch product by ID."""
        doc = self.db.collection("products").document(product_id).get()
        return doc.to_dict() if doc.exists else None
    
    async def get_all_with_filters(self, filters: Dict) -> List[Dict]:
        """Fetch products with DB-level filtering."""
        query = self.db.collection("products")
        
        # Apply filters at database level (OPTIMIZATION)
        if filters.get("category"):
            query = query.where("category", "==", filters["category"])
        if filters.get("max_price"):
            query = query.where("price", "<=", filters["max_price"])
        
        return [doc.to_dict() for doc in query.stream()]
```

**Service Layer** - Business logic separation
```python
# backend/app/services/product_service.py
class ProductService:
    """Business logic for product operations."""
    
    def __init__(self, product_repo: ProductRepository, user_repo: UserRepository):
        self.product_repo = product_repo
        self.user_repo = user_repo
    
    async def get_product_by_id(self, product_id: str, viewer_id: Optional[str] = None):
        """Get product and track view."""
        product = await self.product_repo.get_by_id(product_id)
        
        if viewer_id:
            await self.product_repo.increment_view(product_id, viewer_id)
        
        # Enrich with seller info (prevents N+1 queries)
        product = await self._enrich_with_seller(product)
        
        return product
```

**Dependency Injection** - FastAPI dependencies
```python
# backend/app/api/routes/products.py
from app.api.dependencies.services import get_product_service

@router.get("/{product_id}")
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service),
    current_user: str = Depends(get_optional_user)
):
    """Get product by ID."""
    return await service.get_product_by_id(product_id, current_user)
```

### Frontend Architecture Patterns

**Context API** - Global state management
```javascript
// frontend/src/contexts/AuthContext.jsx
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  
  // Firebase auth state listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setCurrentUser(user);
      if (user) {
        const profile = await fetchUserProfile(user.uid);
        setUserProfile(profile);
      }
    });
    return unsubscribe;
  }, []);
  
  return (
    <AuthContext.Provider value={{ currentUser, userProfile }}>
      {children}
    </AuthContext.Provider>
  );
};
```

**React Query** - Data fetching and caching
```javascript
// frontend/src/pages/BuyerPage.jsx
import { useQuery } from '@tanstack/react-query';

const { data: productsResponse, isLoading } = useQuery({
  queryKey: ['products', filters],
  queryFn: () => getProducts(filters),
  staleTime: 5 * 60 * 1000, // 5 minutes
});

const products = productsResponse?.items || [];
```

**Protected Routes** - Authentication guards
```javascript
// frontend/src/components/ProtectedRoute.jsx
const ProtectedRoute = ({ children }) => {
  const { currentUser, loading } = useAuth();
  
  if (loading) return <LoadingSkeleton />;
  if (!currentUser) return <Navigate to="/login" />;
  if (!currentUser.emailVerified) return <Navigate to="/verify-email" />;
  
  return children;
};
```

### Adding a New Feature

1. **Backend Endpoint**
```python
# backend/app/api/routes/your_feature.py
from fastapi import APIRouter, Depends
from app.schemas.your_feature import YourFeatureCreate, YourFeature
from app.services.your_feature_service import YourFeatureService
from app.api.dependencies.services import get_your_feature_service

router = APIRouter(prefix="/your-feature")

@router.post("", response_model=YourFeature)
async def create_your_feature(
    data: YourFeatureCreate,
    service: YourFeatureService = Depends(get_your_feature_service)
):
    """Create new feature."""
    return await service.create(data)
```

2. **Register Route**
```python
# backend/app/main.py
from app.api.routes import your_feature

app.include_router(your_feature.router, prefix="/api", tags=["your-feature"])
```

3. **Frontend API Call**
```javascript
// frontend/src/services/api.js
export const createYourFeature = async (data) => {
  const response = await api.post('/your-feature', data);
  return response.data;
};
```

4. **Use in Component**
```jsx
// frontend/src/pages/YourFeaturePage.jsx
import { createYourFeature } from '../services/api';

const YourFeaturePage = () => {
  const handleCreate = async (data) => {
    try {
      const result = await createYourFeature(data);
      // Handle success
    } catch (error) {
      // Handle error
    }
  };
  
  return <div>Your Component</div>;
};
```

---

## Key Features Implementation

### AI-Powered Need Board

**Backend Flow**:
1. User submits natural language query
2. `intent_extractor.py` extracts structured data (category, subject, semester, max_price, condition)
3. `semantic_ranker.py` ranks products by match quality (0-100 scale)
4. Results filtered (≥50% match) and limited (top 10)
5. Rate limiting enforced (3 searches/12hrs per user)

**Frontend Flow**:
1. User types query in `NeedBoardPage.jsx`
2. Submit triggers `searchNeedBoard()` API call
3. Display extracted intent and ranked results
4. Update search count from response
5. Refresh history after 500ms

**Security Features**:
- Input sanitization (XSS prevention)
- Output validation (schema enforcement)
- Token budgeting (50k/user/day, 2k/request)
- Rate limiting (3 searches/12hrs)
- Fallback responses on errors

### Demand→Supply Engine

**Backend Flow**:
1. Buyer posts need via `POST /api/needs`
2. AI extracts intent (category, tags, price_range)
3. System matches need to active listings
4. System identifies relevant sellers
5. Top 10 sellers receive notifications
6. Need stored with matched_listings and interested_sellers

**Frontend Flow**:
1. Buyer creates need in `PostNeedPage.jsx`
2. View instant matches
3. Sellers see needs in `SellerDemandFeedPage.jsx`
4. Sellers can message, save, or post item
5. Buyer marks need as fulfilled when satisfied

**Rate Limiting**: 5 needs per day per user

### Real-Time Chat System

**Backend Flow**:
1. Create/get chat room via `POST /api/chats/room`
2. Send message via `POST /api/chats/room/{id}/messages`
3. Fetch messages via `GET /api/chats/room/{id}/messages`
4. Mark as read via `POST /api/chats/messages/{id}/read`

**Frontend Flow** (Optimistic UI):
1. User types message
2. Create temp message with `temp-{timestamp}` ID
3. Add to UI immediately (instant feedback)
4. Send to backend asynchronously
5. Replace temp with real message on success
6. Remove temp and restore text on failure

**Map-Based Merge** (prevents message loss):
```javascript
const mergeMessages = (prev, backendMessages) => {
  const messageMap = new Map(prev.map(m => [m.id, m]));
  
  // Merge backend messages
  backendMessages.forEach(m => messageMap.set(m.id, m));
  
  // Remove confirmed optimistic messages
  const optimisticMessages = prev.filter(m => m._optimistic);
  optimisticMessages.forEach(optMsg => {
    const isConfirmed = backendMessages.some(backendMsg => 
      backendMsg.text === optMsg.text &&
      backendMsg.sender_id === optMsg.sender_id &&
      Math.abs(new Date(backendMsg.timestamp) - new Date(optMsg.timestamp)) < 5000
    );
    
    if (isConfirmed) {
      messageMap.delete(optMsg.id);
    }
  });
  
  // Convert to sorted array
  return Array.from(messageMap.values()).sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );
};
```

---

## Development Workflow

### Adding a New Feature

1. **Backend Endpoint**
```python
# backend/app/api/routes/your_feature.py
from fastapi import APIRouter, Depends
from app.schemas.your_feature import YourFeatureCreate, YourFeature
from app.services.your_feature_service import YourFeatureService
from app.api.dependencies.services import get_your_feature_service

router = APIRouter(prefix="/your-feature")

@router.post("", response_model=YourFeature)
async def create_your_feature(
    data: YourFeatureCreate,
    service: YourFeatureService = Depends(get_your_feature_service)
):
    """Create new feature."""
    return await service.create(data)
```

2. **Register Route**
```python
# backend/main.py
from routes import your_feature

app.include_router(your_feature.router, prefix="/api", tags=["your-feature"])
```

3. **Frontend API Call**
```javascript
// frontend/src/services/api.js
export const yourApiCall = async (data) => {
  const response = await api.post('/your-endpoint', data)
  return response.data
}
```

4. **Use in Component**
```jsx
// frontend/src/pages/YourPage.jsx
import { yourApiCall } from '../services/api'

const YourPage = () => {
  const handleAction = async () => {
    try {
      const result = await yourApiCall(data)
      // Handle success
    } catch (error) {
      // Handle error
    }
  }
  
  return <div>Your Component</div>
}
```

### NeedBoard AI - Demand → Supply Engine

UNIFIND includes an AI-powered demand-supply matching system that connects buyers posting needs with sellers who can fulfill them.

**Key Features**:
- Buyers post needs in natural language (e.g., "need laptop for coding budget 70k")
- AI extracts structured data (category, tags, price range)
- Automatic matching to existing listings and relevant sellers
- Seller demand feed showing ranked buyer needs
- Real-time notifications to relevant sellers

**Architecture**:

**Backend Components**:
1. **Matching Engine** (`backend/services/need_matcher.py`):
   - Text normalization and keyword extraction
   - Scoring algorithm (0-100 points):
     - Category match: 30 points
     - Tag overlap: 25 points
     - Keyword overlap: 30 points
     - Price match: 15 points
   - Functions: `match_need_to_listings()`, `match_need_to_sellers()`, `rank_needs_for_seller()`

2. **API Routes** (`backend/routes/needs.py`):
   ```bash
   POST   /api/needs                  # Create need (5/day limit)
   GET    /api/needs/match/:id        # Get matches for need
   GET    /api/needs/seller-feed      # Get relevant needs for seller
   GET    /api/needs/seller-banner    # Get demand banner data
   POST   /api/needs/:id/fulfill      # Mark need as fulfilled
   POST   /api/needs/:id/save         # Save need (seller interest)
   GET    /api/needs/my-needs         # Get user's needs
   ```

**Frontend Components**:
1. **PostNeedPage** (`/post-need`): Buyers post needs and see instant matches
2. **SellerDemandFeedPage** (`/seller/demand-feed`): Sellers view ranked buyer needs
3. **SellerDemandBanner**: Shows need count on seller dashboard

**Database Schema** (`needs` collection):
```javascript
{
  id: string,
  user_id: string,
  raw_text: string,
  title: string,
  category: string,
  tags: string[],
  price_range: { min: number, max: number },
  college: string,
  status: "open" | "fulfilled" | "expired",
  matched_listings: string[],
  interested_sellers: string[],
  created_at: timestamp
}
```

**How It Works**:
1. Buyer posts need → AI extracts intent (category, tags, price)
2. System matches need to active listings (keyword + category + price scoring)
3. System identifies relevant sellers based on their inventory
4. Top 10 sellers receive notifications
5. Need stored in database with matched listings
6. Sellers view ranked needs in demand feed with relevance scores

**Rate Limiting**: 5 needs per day per user to prevent spam

**Testing**:
```bash
# Test as buyer
# 1. Navigate to /post-need
# 2. Enter: "need laptop for coding budget 70k"
# 3. Verify: structured data extracted, matched listings shown

# Test as seller
# 1. Navigate to /seller (see demand banner if relevant needs exist)
# 2. Click banner → /seller/demand-feed
# 3. Verify: ranked needs shown with relevance scores
# 4. Test actions: Message, Save, Post Item
```

**Performance**: Fast keyword-based matching (<3s), efficient queries (limits to 100 products, 50 needs)

**Security**: All endpoints authenticated, input validation (max 500 chars), rate limiting enforced

### Transaction History System

UNIFIND includes a comprehensive transaction history system that automatically tracks every product status change.

**Key Features**:
- Automatic tracking when products are marked as sold/active
- Complete audit trail of all status changes
- Analytics-ready data for revenue and sales reports
- Seller-specific transaction history

**Database Schema** (`transaction_history` collection):
```javascript
{
  id: "auto-generated",
  amount: 80000.0,                    // Product price
  product_id: "product_id",           // Product ID
  seller_id: "seller_id",             // Seller's user ID
  status: "completed",                // Always "completed"
  transaction_type_sold: true,        // true = sold, false = active
  created_at: Timestamp               // When it happened
}
```

**API Endpoints**:
```bash
# Get transaction history
GET /api/transactions/history?limit=50

# Get statistics
GET /api/transactions/stats?days=30

# Get product history
GET /api/transactions/product/{product_id}
```

**How It Works**:
- When seller marks product as sold → Creates record with `transaction_type_sold: true`
- When seller marks product as active → Creates record with `transaction_type_sold: false`
- Multiple status changes create multiple records, tracking complete lifecycle

**Migration**: Run `python backend/migrate_transaction_history.py` to populate history for existing products.

### Testing

**Backend**
```bash
# Test endpoint
curl -X POST http://localhost:8000/api/your-endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# Check logs
# Logs appear in terminal running main.py
```

**Frontend**
```bash
# Check browser console
# Use React DevTools
# Check Network tab for API calls
```

---

## Performance Optimization

### Chat Polling Optimization
The chat system uses smart visibility-based polling:
- **When visible**: Polls every 5-10 seconds for real-time updates
- **When hidden**: Stops completely to save resources
- **On return**: Immediate refresh + resume polling
- **Benefits**: 90% reduction in API calls when page is hidden

### Request Optimization
- Request deduplication for concurrent identical GET calls
- Auto-retry with exponential backoff for failed requests
- React Query caching (5-minute stale time)
- AbortController support for request cancellation

## Common Tasks

### Add New Pydantic Model
```python
# backend/app/schemas/your_model.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class YourModelBase(BaseModel):
    field1: str
    field2: Optional[int] = None

class YourModelCreate(YourModelBase):
    pass

class YourModel(YourModelBase):
    id: str
    created_at: datetime
```

### Add New Firebase Collection
```python
# In your route
db = get_db()
doc_ref = db.collection('your_collection').document()
doc_ref.set(your_data)
```

### Add Environment Variable
```bash
# 1. Add to backend/.env
YOUR_VAR=value

# 2. Add to backend/app/core/config.py
class Settings(BaseSettings):
    YOUR_VAR: str

# 3. Use in code
from app.core.config import settings
value = settings.YOUR_VAR
```

### Use Recently Viewed Utility
```javascript
// frontend/src/utils/recentlyViewed.js
import { addToRecentlyViewed, getRecentlyViewed, clearRecentlyViewed } from '../utils/recentlyViewed';

// Add product to recently viewed
const handleProductView = (product) => {
  addToRecentlyViewed(product);
  navigate(`/listing/${product.id}`);
};

// Get recently viewed products
const recentProducts = getRecentlyViewed();

// Clear history
clearRecentlyViewed();
```



### Email Verification System

UNIFIND uses a custom Gmail-based email verification system instead of Firebase's built-in verification.

**Architecture**:
```
User Signs Up → Backend Sends Email (Gmail SMTP) → User Clicks Link → 
Backend Verifies Token → Updates Firestore + Firebase Auth → User Verified
```

**Backend Components**:

1. **Email Service** (`backend/services/email_service.py`):
```python
from services.email_service import email_service

# Generate verification token
token = email_service.generate_verification_token(user_email)

# Send verification email
verification_url = f"{frontend_url}/verify-email?token={token}"
await email_service.send_verification_email(user_email, verification_url)

# Verify token
email = email_service.verify_token(token)  # Returns email or None

# Invalidate token after use
email_service.invalidate_token(token)
```

2. **Auth Routes** (`backend/routes/auth.py`):
- `POST /api/auth/send-verification` - Send verification email
- `POST /api/auth/verify-email` - Verify email with token
- `POST /api/auth/resend-verification` - Resend verification email

**Frontend Components**:

1. **Signup Flow** (`frontend/src/pages/SignupPage.jsx`):
```javascript
// After creating user with Firebase Auth
const userCredential = await signup(email, password, ...);

// Send verification email via backend
await fetch(`${import.meta.env.VITE_API_URL}/auth/send-verification`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: email,
    firebase_uid: userCredential.user.uid
  })
});
```

2. **Verify Email Page** (`frontend/src/pages/VerifyEmailPage.jsx`):
```javascript
// Extracts token from URL and verifies
const token = searchParams.get('token');
const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/verify-email`, {
  method: 'POST',
  body: JSON.stringify({ token })
});
```

3. **Auto-Check Verification** (`frontend/src/components/ProtectedRoute.jsx`):
```javascript
// Checks verification status every 5 seconds
useEffect(() => {
  const checkVerificationStatus = async () => {
    await reload(currentUser);
    if (currentUser.emailVerified) {
      await syncEmailVerificationStatus(currentUser);
      window.location.reload();
    }
  };
  const interval = setInterval(checkVerificationStatus, 5000);
  return () => clearInterval(interval);
}, [currentUser]);
```

**Configuration**:

1. **Backend** (`backend/.env`):
```env
GMAIL_USER=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
```

2. **Gmail App Password Setup**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Generate password for "Mail"
   - Copy 16-character password (no spaces)

**Security Features**:
- 24-hour token expiry
- One-time use tokens (invalidated after verification)
- Secure token generation using `secrets.token_urlsafe(32)`
- Syncs verification between Firebase Auth and Firestore
- SMTP over TLS (port 587)

**Testing**:
```bash
# Test email service
cd backend
python -c "from services.email_service import email_service; print(email_service.sender_email)"

# Test sending email (update with your email)
python -c "
import asyncio
from services.email_service import email_service
asyncio.run(email_service.send_verification_email(
    'test@example.com',
    'http://localhost:5173/verify-email?token=test123'
))
"
```

**Troubleshooting**:
- **Email not sending**: Check Gmail credentials, ensure App Password is used
- **Token invalid**: Tokens expire after 24 hours, generate new one
- **Verification not syncing**: Check backend logs for Firebase Auth update errors
- **Emails in spam**: Add sender to contacts, check email template

### Implement Advanced Filtering
```javascript
// Use useMemo for performance
const filteredProducts = useMemo(() => {
  return products.filter(product => {
    // Search filter
    if (searchQuery && !product.title.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Category filter
    if (selectedCategory !== 'All' && product.category !== selectedCategory) {
      return false;
    }
    
    return true;
  }).sort((a, b) => {
    // Sorting logic
    if (sortBy === 'price-low') return a.price - b.price;
    if (sortBy === 'price-high') return b.price - a.price;
    return 0;
  });
}, [products, searchQuery, selectedCategory, sortBy]);
```

### Optimize AI Prompt
```python
# backend/services/your_ai_service.py
SYSTEM_PROMPT = """Short, clear instructions"""

def _build_prompt(query: str) -> str:
    # Truncate long inputs
    query = query[:200]
    
    return f"Task: {query}\nOutput: JSON only"
```

### Avoid Common Performance Pitfalls
```javascript
// ❌ BAD: Recreating static data on every render
const MyComponent = () => {
  const emojis = { /* large object */ }; // Recreated every render!
  
  return <div>{/* ... */}</div>
}

// ✅ GOOD: Move static data outside component
const EMOJIS = { /* large object */ }; // Created once

const MyComponent = () => {
  return <div>{/* ... */}</div>
}

// ❌ BAD: Multiple expensive calculations in JSX
return (
  <div>
    {isOnline(messages, userId) && <Badge />}
    <Status online={isOnline(messages, userId)} />
    <Text>{isOnline(messages, userId) ? 'Online' : 'Offline'}</Text>
  </div>
)

// ✅ GOOD: Compute once, reuse
const online = isOnline(messages, userId);
return (
  <div>
    {online && <Badge />}
    <Status online={online} />
    <Text>{online ? 'Online' : 'Offline'}</Text>
  </div>
)

// ❌ BAD: N+1 query pattern
const ChatList = ({ chats }) => {
  return chats.map(chat => {
    const messages = await getMessages(chat.id); // Fetches for every chat!
    return <ChatItem messages={messages} />
  })
}

// ✅ GOOD: Fetch data at parent level or use caching
const ChatList = ({ chats, messagesCache }) => {
  return chats.map(chat => {
    const messages = messagesCache[chat.id]; // Use cached data
    return <ChatItem messages={messages} />
  })
}
```

---

## Performance Optimization - Buyer/Seller Pages

### Backend-Driven Architecture

UNIFIND uses a backend-driven architecture that eliminates N+1 queries and reduces API calls by 95%.

**Key Improvements**:
- Server-side filtering, sorting, and pagination
- Seller info embedded in product responses (no N+1 queries)
- Batch API for recently viewed products
- Clean state management (15+ variables → 4 objects)

**Performance Metrics**:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| API Calls (20 products) | 27+ | 2 | 93% ↓ |
| Page Load Time | 4-5s | <500ms | 90% ↓ |
| Data Transfer | 500KB | 100KB | 80% ↓ |
| State Variables | 15+ | 4 | 73% ↓ |

**Backend Enhancements**:
```python
# Enrich products with seller info (eliminates N+1)
def enrich_product_with_seller(db, product_data: dict) -> dict:
    seller_id = product_data.get('seller_id')
    # Fetch seller + profile in one go
    product_data['seller'] = {
        'id': seller_id,
        'name': user_data.get('name'),
        'avatar': avatar
    }
    return product_data

# Batch endpoint for recently viewed
@router.post("/batch", response_model=List[Product])
async def get_products_batch(product_ids: List[str]):
    # Fetch up to 50 products in ONE request
    # Returns enriched products with seller info
```

**Frontend Optimization**:
```javascript
// Backend handles ALL filtering/sorting
const queryParams = useMemo(() => ({
  q: appliedSearch,
  category: filters.category !== 'All' ? filters.category : undefined,
  condition: filters.condition !== 'all' ? filters.condition : undefined,
  sort: sortBy,
  page: 1,
  page_size: 100,
}), [appliedSearch, filters, sortBy]);

const { data: productsResponse } = useProducts(queryParams);
const products = productsResponse?.items || []; // Already filtered & sorted!

// Recently viewed - 1 batch call instead of N calls
const { data: recentlyViewedProducts = [] } = useProductsBatch(
  recentlyViewedIds.slice(0, 6)
);
```

**Performance Metrics**:
- API calls reduced by 93% (40+ → 2-3 per page)
- Page load time: 500ms → 100ms (80% faster)
- AI search time: 25s → 10s (60% faster)
- Server CPU usage: 60% reduction
- Memory usage: 40% reduction

---

## React Best Practices

### Preventing Memory Leaks
Always clean up effects that set state or create subscriptions:

```javascript
// ✅ GOOD: Proper cleanup with isActive flag
useEffect(() => {
  let isActive = true;
  
  const loadData = async () => {
    const data = await fetchData();
    if (isActive) {
      setState(data); // Only update if component is still mounted
    }
  };
  
  loadData();
  
  return () => {
    isActive = false; // Prevent state updates after unmount
  };
}, []);

// ✅ GOOD: Cleanup intervals
useEffect(() => {
  const interval = setInterval(() => {
    fetchUpdates();
  }, 5000);
  
  return () => {
    clearInterval(interval); // Always clear intervals
  };
}, []);
```

### Avoiding Race Conditions
Prevent stale closures in async operations:

```javascript
// ❌ BAD: Stale closure in interval
useEffect(() => {
  const interval = setInterval(() => {
    loadChats(friendsOnly); // friendsOnly is stale!
  }, 10000);
  
  return () => clearInterval(interval);
}, []); // Missing friendsOnly dependency

// ✅ GOOD: Use inline arrow function
useEffect(() => {
  const interval = setInterval(() => {
    loadChats(friendsOnly); // Always uses current value
  }, 10000);
  
  return () => clearInterval(interval);
}, [friendsOnly]); // Include dependency

// ✅ BETTER: Use ref for mutable values
const friendsOnlyRef = useRef(friendsOnly);
friendsOnlyRef.current = friendsOnly;

useEffect(() => {
  const interval = setInterval(() => {
    loadChats(friendsOnlyRef.current); // Always current
  }, 10000);
  
  return () => clearInterval(interval);
}, []); // No dependency needed
```

### Preventing Infinite Loops
Be careful with useEffect dependencies:

```javascript
// ❌ BAD: Callback in dependency array
const ChatItem = ({ onProfileLoaded }) => {
  useEffect(() => {
    loadProfile();
    onProfileLoaded(profile); // Triggers parent re-render
  }, [onProfileLoaded]); // Parent recreates this every render!
}

// ✅ GOOD: Wrap callback in useCallback
const ParentComponent = () => {
  const handleProfileLoaded = useCallback((profile) => {
    setProfiles(prev => ({ ...prev, [profile.id]: profile }));
  }, []); // Stable reference
  
  return <ChatItem onProfileLoaded={handleProfileLoaded} />
}

// ✅ BETTER: Remove callback from dependencies if not needed
const ChatItem = ({ onProfileLoaded }) => {
  useEffect(() => {
    loadProfile();
    onProfileLoaded(profile);
  }, []); // Only run once
}
```

### Optimizing Re-renders
Use React.memo and useMemo strategically:

```javascript
// ✅ Memoize expensive components
const ChatListItem = React.memo(({ chat, onClick }) => {
  return <div onClick={onClick}>{chat.name}</div>
}, (prevProps, nextProps) => {
  // Only re-render if chat.id changed
  return prevProps.chat.id === nextProps.chat.id;
});

// ✅ Memoize expensive computations
const filteredChats = useMemo(() => {
  return chats.filter(chat => 
    chat.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
}, [chats, searchQuery]); // Only recompute when these change

// ✅ Memoize callbacks passed to children
const handleChatClick = useCallback((chatId) => {
  setSelectedChat(chatId);
}, []); // Stable reference
```

### Proper Cleanup Patterns
```javascript
// ✅ Complete cleanup example
useEffect(() => {
  let isActive = true;
  const controller = new AbortController();
  
  const loadData = async () => {
    try {
      const data = await fetch('/api/data', {
        signal: controller.signal
      });
      
      if (isActive) {
        setState(data);
      }
    } catch (error) {
      if (error.name !== 'AbortError' && isActive) {
        setError(error);
      }
    }
  };
  
  const interval = setInterval(loadData, 5000);
  loadData(); // Initial load
  
  return () => {
    isActive = false;
    controller.abort(); // Cancel pending requests
    clearInterval(interval); // Clear interval
  };
}, []);
```

---

## Chat System Architecture

### Core Principles

1. **Single Source of Truth**: Backend generates all authoritative data
2. **Deterministic IDs**: `chat_room_id = {min_user}_{max_user}_{product_id?}`
3. **Map-Based Merge**: Never blindly overwrite state, always merge with existing messages
4. **Optimistic UI**: Instant feedback with temporary IDs, replaced on confirmation

### Implementation Pattern

**Optimistic Message Flow**:
1. Create temp message with `temp-{timestamp}` ID
2. Add to UI immediately for instant feedback
3. Send to backend asynchronously
4. Replace temp with real message on success
5. Remove temp and restore text on failure

**Map-Based Merge** (prevents message loss):
```javascript
// Create Map from existing messages
const messageMap = new Map(prev.map(m => [m.id, m]));

// Merge backend messages
backendMessages.forEach(m => messageMap.set(m.id, m));

// Remove confirmed optimistic messages
// Convert to sorted array
return Array.from(messageMap.values()).sort(byTimestamp);
```

**Common Mistakes**:
- ❌ Blindly overwriting state: `setMessages(fetchedMessages)`
- ❌ Generating chat_room_id in frontend (order-dependent)
- ❌ No message status indicators
- ❌ No deduplication logic

**Best Practices**:
- ✅ Let backend generate deterministic IDs
- ✅ Use Map for O(1) deduplication
- ✅ Show status for user feedback
- ✅ Proper cleanup in useEffect

> **Full Implementation**: See `frontend/src/pages/ChatPage.jsx` for complete production codeend messages (replaces optimistic if confirmed)
    chatMessages.forEach(msg => {
      messageMap.set(msg.id, { ...msg, status: 'sent' });
    });
    
    // Remove optimistic messages that have been confirmed
    const optimisticMessages = prev.filter(m => m._optimistic);
    optimisticMessages.forEach(optMsg => {
      const isConfirmed = chatMessages.some(backendMsg => 
        backendMsg.text === optMsg.text &&
        backendMsg.sender_id === optMsg.sender_id &&
        Math.abs(new Date(backendMsg.timestamp) - new Date(optMsg.timestamp)) < 5000
      );
      
      if (isConfirmed) {
        messageMap.delete(optMsg.id);
      }
    });
    
    // Convert to sorted array
    return Array.from(messageMap.values()).sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  });
};
```

### Why This Works

1. **No Overwrites**: Map preserves existing messages
2. **No Duplicates**: Map dedup by ID (O(1) lookup)
3. **Optimistic Survives**: Kept until confirmed by backend
4. **Correct Order**: Sorted by timestamp after merge
5. **Error Recovery**: Failed messages removed, text restored

### Common Mistakes to Avoid

```javascript
// ❌ Generating chat_room_id in frontend
const chatRoomId = `${user1}_${user2}`; // Order-dependent!

// ✅ Let backend generate deterministic ID
const chatRoom = await getOrCreateChatRoom(user1, user2);

// ❌ Overwriting state on polling
setMessages(fetchedMessages);

// ✅ Merge with existing state
setMessages(prev => mergeMessages(prev, fetchedMessages));

// ❌ No message status
<div>{message.text}</div>

// ✅ Show status for feedback
<div>
  {message.text}
  {message._optimistic && <span>Sending...</span>}
</div>

// ❌ No deduplication
messages.push(newMessage);

// ✅ Deduplicate by ID
const map = new Map(messages.map(m => [m.id, m]));
map.set(newMessage.id, newMessage);
```

### Testing Chat System

```javascript
// Test 1: Message persistence
test('message persists after polling', async () => {
  await sendMessage('Hello');
  await waitFor(() => expect(screen.getByText('Hello')).toBeInTheDocument());
  
  // Simulate polling
  await act(() => pollMessages());
  
  // Message should still be there
  expect(screen.getByText('Hello')).toBeInTheDocument();
});

// Test 2: No duplicates
test('no duplicate messages', async () => {
  await sendMessage('Hello');
  await act(() => pollMessages());
  
  const messages = screen.getAllByText('Hello');
  expect(messages).toHaveLength(1);
});

// Test 3: Optimistic UI
test('message appears immediately', async () => {
  const promise = sendMessage('Hello');
  
  // Should appear before promise resolves
  expect(screen.getByText('Hello')).toBeInTheDocument();
  
  await promise;
});
```

---

## Debugging

### Backend Issues

**Check Logs**
```bash
# Terminal running uvicorn shows all logs
# Look for ERROR or WARNING messages
```

**Common Issues**
1. **Firebase connection fails**
   - Check .env has all Firebase variables
   - Verify FIREBASE_PRIVATE_KEY has \n for newlines

2. **Email verification not working**
   - Check GMAIL_USER and GMAIL_APP_PASSWORD in .env
   - Verify Gmail App Password is generated (not regular password)
   - Test with: `python -c "from services.email_service import email_service; print(email_service.sender_email)"`
   - Check backend logs for SMTP errors
   - Verify emails aren't going to spam folder

3. **Gemini API errors**
   - Check GEMINI_API_KEY is valid
   - Verify API quota not exceeded

4. **CORS errors**
   - Check CORS_ORIGINS includes frontend URL
   - Restart backend after changing .env

5. **404 errors on new endpoints**
   - Backend server needs restart to load new routes
   - Stop server (Ctrl+C) and restart: `uvicorn app.main:app --reload`
   - Verify routes are registered in `backend/app/main.py`
   - Check `backend/app/api/routes/__init__.py` includes all route modules

6. **Module import errors**
   - Verify file exists in correct location
   - Check `__init__.py` files exist in all package directories
   - Restart backend server after adding new modules

### Frontend Issues

**Check Browser Console**
```javascript
// Add debug logs
console.log('Data:', data)
console.error('Error:', error)
```

**Common Issues**
1. **API calls fail**
   - Check VITE_API_URL is correct
   - Verify backend is running
   - Check Network tab for error details

2. **Firebase auth fails**
   - Check all VITE_FIREBASE_* variables
   - Verify Firebase project is active

3. **Email verification not detected**
   - Wait 5 seconds for auto-check to run
   - Click "I've Verified My Email" button manually
   - Check browser console for errors
   - Verify token hasn't expired (24 hours)
   - Try logging out and back in

4. **Build fails**
   - Delete node_modules and reinstall
   - Check for syntax errors

5. **Products not displaying**
   - Check if backend returns paginated response: `{items: [], total, page}`
   - Frontend should extract `items` array from response
   - Verify `is_active` field filtering is correct

6. **Status checks not working**
   - Use explicit checks: `is_active === true` (not `!== false`)
   - Buyers should only see `is_active === true` products
   - Sellers can see all products with proper filtering

### Quick Restart Procedures

**Backend Restart** (fixes most 404 and module errors):
```bash
# Stop current server (Ctrl+C)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Restart**:
```bash
# Stop current server (Ctrl+C)
cd frontend
npm run dev
```

**Complete Reset**:
```bash
# Backend
cd backend
rm -rf __pycache__ */__pycache__
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## Performance Tips

### Backend
1. **Use caching** - Gemini client has built-in cache
2. **Limit queries** - Use .limit() on Firestore queries
3. **Async everything** - Use async/await properly
4. **Optimize prompts** - Shorter prompts = faster + cheaper

### Frontend
1. **Lazy load pages** - Use React.lazy()
2. **Memoize expensive computations** - Use useMemo()
3. **Debounce inputs** - Especially for search
4. **Optimize images** - Compress before upload

---

## Security Best Practices

### Backend
1. **Never commit .env** - Already in .gitignore
2. **Validate all inputs** - Use Pydantic models
3. **Rate limit AI endpoints** - Already implemented
4. **Use HTTPS in production** - Automatic on Render

### Frontend
1. **Never expose API keys** - Use VITE_ prefix for public vars
2. **Validate user input** - Before sending to backend
3. **Handle errors gracefully** - Don't expose error details
4. **Use Firebase Auth** - Don't roll your own

---

## Deployment

### Quick Deploy

**Backend (Render)**
```bash
# 1. Push to GitHub
git push origin main

# 2. Create Render web service
# 3. Set environment variables
# 4. Deploy
```

**Frontend (Vercel)**
```bash
# 1. Push to GitHub
git push origin main

# 2. Import project in Vercel
# 3. Set environment variables
# 4. Deploy
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## Performance Optimization

### Database Query Optimization

**N+1 Query Problem Fixed**:
The product listing endpoint was making 40+ database queries per page (2 queries per product for seller info). This has been optimized to use batch queries:

```python
# backend/routes/products.py
# Uses enrich_products_with_sellers_batch() instead of individual queries
# Reduces 40 queries to 2-3 per page load
```

**Performance Impact**:
- Product listing: 500ms → 100ms (80% faster)
- Database queries: 40+ → 2-3 per page (93% reduction)

### AI Search Optimization

**Pre-filtering Before AI**:
The Need Board AI search now pre-filters products before sending to Gemini:

```python
# backend/routes/need_board.py
# 1. Extract intent first
# 2. Filter by category if specified
# 3. Filter by max_price if specified
# 4. Send only relevant products (50 instead of 100)
```

**Performance Impact**:
- AI search: 25s → 10s (60% faster)
- Reduced API costs by 50%

### Caching Strategy

A simple in-memory cache module is available (`backend/cache.py`):

```python
from cache import cached, USER_PROFILE_TTL

@cached(ttl=USER_PROFILE_TTL, key_prefix="user_profile")
def get_user_profile(user_id):
    # Expensive database query
    return profile
```

**Cache TTLs**:
- User profiles: 1 hour
- Product listings: 5 minutes
- Seller info: 30 minutes

**For Production**: Replace with Redis for distributed caching

### Monitoring Performance

**Check Response Times**:
```bash
# Backend logs show response times
tail -f backend/logs/app.log | grep "←"

# Example output:
← GET /api/products [200] 0.087s
```

**Slow Query Detection**:
```bash
# Find queries taking > 1 second
tail -f backend/logs/app.log | grep -E "\d\.\d{3,}s"
```

**Cache Statistics** (if implemented):
```bash
curl http://localhost:8000/admin/cache-stats
```

---

## Troubleshooting

### Product Delete Not Working

**Symptoms**: Delete button doesn't remove product

**Debug Steps**:
1. Open browser DevTools (F12) → Console tab
2. Look for logs starting with `[SellerPage]`, `[Hook]`, `[API]`
3. Check Network tab for DELETE request to `/api/products/{id}`

**Common Issues**:
- **401 Unauthorized**: User not logged in or token expired
- **403 Forbidden**: User doesn't own the product
- **404 Not Found**: Product doesn't exist
- **500 Server Error**: Backend error (check backend logs)

**Quick Test**:
```javascript
// In browser console
const token = await firebase.auth().currentUser.getIdToken();
fetch('http://localhost:8000/api/products/PRODUCT_ID', {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(console.log)
.catch(console.error);
```

### Server Performance Issues

**Symptoms**: Slow response times, high CPU/memory usage

**Check**:
1. Verify Firestore indexes are deployed and enabled
2. Check for N+1 query patterns in logs
3. Monitor response times in backend logs

**Quick Fixes**:
```bash
# 1. Restart backend
cd backend
pkill -f "uvicorn main:app"
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Deploy indexes (if not done)
firebase deploy --only firestore:indexes

# 3. Verify performance
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/api/products
# Should be < 0.2s
```

**Performance Checklist**:
- [ ] Firestore indexes deployed and enabled
- [ ] Batch queries used for seller enrichment
- [ ] AI pre-filtering enabled
- [ ] Response times < 200ms for product listing
- [ ] No N+1 query patterns in logs

### "Module not found" errors
```bash
# Backend
pip install -r requirements.txt

# Frontend
rm -rf node_modules package-lock.json
npm install
```

### "Port already in use"
```bash
# Find and kill process
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### "Firebase not initialized"
```bash
# Check .env file exists
ls backend/.env

# Check Firebase variables are set
cat backend/.env | grep FIREBASE
```

### "Gemini API timeout"
```bash
# Check API key
cat backend/.env | grep GEMINI

# Test API key
curl https://generativelanguage.googleapis.com/v1/models?key=YOUR_KEY
```

---

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Use async/await for I/O operations

```python
async def your_function(param: str) -> dict:
    """
    Brief description.
    
    Args:
        param: Description
        
    Returns:
        dict: Description
    """
    # Implementation
    return result
```

### JavaScript (Frontend)
- Use ES6+ features
- Functional components with hooks
- Destructure props
- Use const/let (not var)

```javascript
const YourComponent = ({ prop1, prop2 }) => {
  const [state, setState] = useState(null)
  
  useEffect(() => {
    // Side effects
  }, [dependencies])
  
  return <div>Content</div>
}
```

---

## Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Firebase Docs](https://firebase.google.com/docs)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [Firebase Console](https://console.firebase.google.com/)
- [Render Dashboard](https://dashboard.render.com/)
- [Vercel Dashboard](https://vercel.com/dashboard)

---

## Getting Help

1. **Check Documentation**
   - README.md - Project overview
   - DEPLOYMENT.md - Deployment guide
   - This file - Development guide

2. **Check Logs**
   - Backend: Terminal output
   - Frontend: Browser console
   - Production: Render/Vercel dashboards

3. **Search Issues**
   - GitHub Issues
   - Stack Overflow
   - Framework documentation

4. **Ask Team**
   - Email: systemrecord07@gmail.com
   - GitHub: Open an issue

---

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open Pull Request

---

**Happy Coding! 🚀**

Last Updated: May 15, 2026  
Version: 2.4.5
