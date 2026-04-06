"""
AI Need Board API - Optimized with rate limiting and error handling.
"""
import time
import logging
from typing import Dict
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse

from models import NeedBoardRequest, NeedBoardResponse, ExtractedIntent, RankedResult
from services.mock_listings import MOCK_LISTINGS
from services.intent_extractor import extract_intent
from services.semantic_ranker import rank_listings
from services.gemini_client import GeminiAPIError, GeminiTimeoutError

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiting: track last request time per IP
_last_request_time: Dict[str, float] = {}
RATE_LIMIT_SECONDS = 10  # 1 request per 10 seconds per IP
MAX_QUERY_LENGTH = 500  # Maximum query length


# Explicit OPTIONS handler for need-board
@router.api_route("/need-board", methods=["OPTIONS"])
async def need_board_options():
    """Handle CORS preflight for need-board endpoint."""
    return JSONResponse(
        content={"status": "ok"},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.post("/need-board", response_model=NeedBoardResponse)
async def need_board(request: NeedBoardRequest, req: Request):
    """
    AI-powered Need Board endpoint.
    Extracts intent from natural language and ranks matching products.
    
    Rate limited to 1 request per 10 seconds per IP.
    """
    # Rate limiting check
    client_ip = req.client.host
    current_time = time.time()
    
    if client_ip in _last_request_time:
        time_since_last = current_time - _last_request_time[client_ip]
        if time_since_last < RATE_LIMIT_SECONDS:
            wait_time = int(RATE_LIMIT_SECONDS - time_since_last)
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Please wait {wait_time} seconds."
            )
    
    # Update last request time
    _last_request_time[client_ip] = current_time
    
    # Validate query
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    if len(request.query) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query too long. Maximum {MAX_QUERY_LENGTH} characters."
        )
    
    try:
        logger.info(f"Processing need board query: {request.query[:50]}...")
        
        # Extract intent from query
        intent = await extract_intent(request.query)
        logger.debug(f"Extracted intent: {intent}")
        
        # Rank listings against intent
        ranked = await rank_listings(request.query, intent, MOCK_LISTINGS)
        logger.debug(f"Ranked {len(ranked)} listings")
        
        # Enrich results with listing details
        listing_map = {str(l["id"]): l for l in MOCK_LISTINGS}
        enriched = []
        
        for r in ranked:
            listing = listing_map.get(str(r.get("id", "")), {})
            enriched.append(RankedResult(
                **r,
                title=listing.get("title"),
                price=listing.get("price"),
            ))
        
        logger.info(f"Successfully processed query with {len(enriched)} results")
        
        return NeedBoardResponse(
            extracted=ExtractedIntent(**intent),
            rankedResults=enriched,
        )
        
    except GeminiTimeoutError as exc:
        logger.error(f"Gemini API timeout: {exc}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI service timeout. Please try again."
        )
        
    except GeminiAPIError as exc:
        logger.error(f"Gemini API error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again later."
        )
        
    except ValueError as exc:
        logger.error(f"Value error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
        
    except Exception as exc:
        logger.error(f"Unexpected error in need_board: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )
