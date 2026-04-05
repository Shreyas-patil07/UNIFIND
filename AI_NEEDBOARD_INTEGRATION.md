# AI NeedBoard Integration

## Overview
The AI-powered NeedBoard feature has been successfully integrated into this project. It uses Google's Gemini 2.5 Flash model to understand natural language queries and match them with relevant product listings.

## What's Included

### Backend Files Added:

1. **Services** (`backend/services/`)
   - `gemini_client.py` - Handles Gemini API communication
   - `intent_extractor.py` - Extracts structured intent from user queries
   - `semantic_ranker.py` - Ranks listings based on relevance
   - `mock_listings.py` - Sample product listings for testing
   - `__init__.py` - Package initialization

2. **Routes** (`backend/routes/`)
   - `need_board.py` - API endpoint for NeedBoard functionality

3. **Models** (`backend/models.py`)
   - `NeedBoardRequest` - Request model
   - `ExtractedIntent` - Extracted user intent structure
   - `RankedResult` - Ranked product result
   - `NeedBoardResponse` - Response model

4. **Configuration**
   - Updated `main.py` to include need_board router
   - Updated `requirements.txt` to include `google-generativeai`
   - Updated `.env` with `GEMINI_API_KEY`

## How It Works

1. User enters a natural language query (e.g., "I need a laptop for coding under 50000")
2. Backend extracts structured intent (category, subject, price, condition, etc.)
3. Gemini AI ranks available listings based on relevance
4. Returns top matches with match scores and reasons

## API Endpoint

**POST** `/api/need-board`

Request:
```json
{
  "query": "I need a laptop for coding under 50000"
}
```

Response:
```json
{
  "extracted": {
    "category": "Electronics",
    "subject": "Laptop",
    "semester": "Not specified",
    "max_price": 50000.0,
    "condition": "Any",
    "intent_summary": "User wants a laptop for coding..."
  },
  "rankedResults": [
    {
      "id": "1",
      "match_score": 85,
      "reason": "Matches budget and purpose",
      "title": "Dell Inspiron 15 Laptop",
      "price": 28000
    }
  ]
}
```

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Verify Environment Variables**
   Make sure `backend/.env` has:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Start Backend**
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Test the Endpoint**
   ```bash
   curl -X POST http://localhost:8000/api/need-board \
     -H "Content-Type: application/json" \
     -d '{"query":"I need a laptop for coding under 50000"}'
   ```

## Frontend Integration

The frontend already has the NeedBoard page (`frontend/src/pages/NeedBoardPage.jsx`) that connects to this backend endpoint through the API service (`frontend/src/services/api.js`).

Make sure your `frontend/.env` has:
```
VITE_API_URL=http://localhost:8000/api
```

## Features

- Natural language query understanding
- Intelligent intent extraction
- Semantic ranking of products
- Error handling for timeouts and API failures
- Mock data for testing (can be replaced with real database queries)

## Technology Stack

- **AI Model**: Google Gemini 2.5 Flash
- **Backend**: FastAPI, Python
- **Frontend**: React, Vite
- **API**: RESTful JSON API
