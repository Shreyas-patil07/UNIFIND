# Server Performance Optimization Plan

## Critical Issues Identified

### 1. N+1 Query Problem (MOST CRITICAL)
**Impact**: 40+ database queries per page load instead of 2-3

**Location**: `backend/routes/products.py` - `enrich_product_with_seller()`
- Called for every product in results
- Makes 2 Firestore queries per product (users + profiles)
- For 20 products = 40 queries!

### 2. Missing Database Indexes
**Impact**: Full collection scans on every query

Queries without indexes:
- Products by is_active + mark_as_sold
- Needs by user_id + created_at
- Friendships by user_id + status
- Transactions by seller_id + created_at

### 3. Expensive AI Operations
**Impact**: 20-30 second response times

- Fetches 100 products for every AI search
- No persistent cache (clears on restart)
- No pre-filtering before sending to AI

### 4. Inefficient Product Filtering
**Impact**: Fetches ALL products then filters in Python

- Should use Firestore queries
- Search done with string contains
- Sorting done in Python

## Immediate Fixes (Apply Now)

### Fix 1: Batch Seller Enrichment
Replace N+1 queries with batch fetch

### Fix 2: Add Firestore Indexes
Create composite indexes for common queries

### Fix 3: Add Response Caching
Cache frequently accessed data

### Fix 4: Optimize Product Queries
Use Firestore filtering instead of Python

### Fix 5: Pre-filter Before AI
Reduce data sent to Gemini

## Implementation Order

1. **NOW**: Fix N+1 queries (biggest impact)
2. **NOW**: Add database indexes
3. **NEXT**: Add caching layer
4. **NEXT**: Optimize AI operations
5. **LATER**: Background job queue for emails
