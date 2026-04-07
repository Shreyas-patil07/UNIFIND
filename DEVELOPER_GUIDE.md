# UNIFIND - Developer Guide

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Firebase project with Firestore
- Gemini API key

### Setup

1. **Clone and Install**
```bash
git clone https://github.com/Shreyas-patil07/UNIFIND.git
cd UNIFIND

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend (new terminal)
cd frontend
npm install
```

2. **Configure Environment**
```bash
# Backend: Copy and edit .env
cd backend
cp .env.example .env
# Edit .env with your Firebase and Gemini credentials

# Frontend: Copy and edit .env
cd frontend
cp .env.example .env
# Edit .env with your Firebase client config
```

3. **Run**
```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

4. **Access**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Project Structure

```
UNIFIND/
├── backend/                    # FastAPI Backend
│   ├── routes/                # API endpoints
│   │   ├── products.py       # Product CRUD
│   │   ├── users.py          # User management
│   │   ├── chats.py          # Messaging
│   │   ├── reviews.py        # Reviews
│   │   └── need_board.py     # AI matching
│   ├── services/             # Business logic
│   │   ├── gemini_client.py  # AI client
│   │   ├── intent_extractor.py
│   │   ├── semantic_ranker.py
│   │   └── mock_listings.py
│   ├── config.py             # Configuration
│   ├── database.py           # Firebase init
│   ├── models.py             # Pydantic models
│   ├── main.py               # App entry point
│   └── requirements.txt      # Dependencies
│
├── frontend/                  # React + Vite
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── contexts/         # React contexts
│   │   ├── pages/            # Page components
│   │   ├── services/         # API clients
│   │   ├── utils/            # Utilities
│   │   │   ├── cn.js         # Class name merger
│   │   │   ├── constants.js  # App constants
│   │   │   └── recentlyViewed.js  # Recently viewed tracking
│   │   ├── App.jsx           # Main app
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Dependencies
│   └── vite.config.js        # Vite config
│
└── docs/                      # Documentation
    ├── DEPLOYMENT.md         # Deployment guide
    ├── REFACTORING_SUMMARY.md
    └── DEVELOPER_GUIDE.md    # This file
```

---

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React 18 + Vite 5
- **Database**: Firebase Firestore
- **AI**: Google Gemini API
- **Styling**: Tailwind CSS
- **Deployment**: Render (backend) + Vercel (frontend)

### Data Flow
```
User Input → Frontend → Backend API → Firebase/Gemini → Response
```

### Database Collections
1. **users** - Core authentication data
2. **user_profiles** - Extended user info (public/private)
3. **products** - Product listings
4. **chat_rooms** - Chat metadata
5. **messages** - Chat messages
6. **reviews** - User reviews
7. **transaction_history** - Buy/sell records

---

## Development Workflow

### Adding a New Feature

1. **Backend Endpoint**
```python
# backend/routes/your_feature.py
from fastapi import APIRouter, HTTPException
from models import YourModel
from database import get_db

router = APIRouter()

@router.post("/your-endpoint")
async def your_endpoint(data: YourModel):
    db = get_db()
    # Your logic here
    return {"status": "success"}
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

## Common Tasks

### Add New Pydantic Model
```python
# backend/models.py
from pydantic import BaseModel
from typing import Optional

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

# 2. Add to backend/config.py
class Settings(BaseSettings):
    YOUR_VAR: str

# 3. Use in code
from config import settings
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

## Debugging

### Backend Issues

**Check Logs**
```bash
# Terminal running main.py shows all logs
# Look for ERROR or WARNING messages
```

**Common Issues**
1. **Firebase connection fails**
   - Check .env has all Firebase variables
   - Verify FIREBASE_PRIVATE_KEY has \n for newlines

2. **Gemini API errors**
   - Check GEMINI_API_KEY is valid
   - Verify API quota not exceeded

3. **CORS errors**
   - Check CORS_ORIGINS includes frontend URL
   - Restart backend after changing .env

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

3. **Build fails**
   - Delete node_modules and reinstall
   - Check for syntax errors

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

## Troubleshooting

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

Last Updated: April 6, 2026
