from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models import NeedBoardRequest, NeedBoardResponse, ExtractedIntent, RankedResult
from services.mock_listings import MOCK_LISTINGS
from services.intent_extractor import extract_intent
from services.semantic_ranker import rank_listings
from services.gemini_client import GeminiAPIError, GeminiTimeoutError

router = APIRouter()


@router.post("/need-board", response_model=NeedBoardResponse)
async def need_board(request: NeedBoardRequest):
    # Validate query is non-empty / non-whitespace
    if not request.query or not request.query.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid query", "detail": "Query must be a non-empty, non-whitespace string."},
        )

    try:
        intent = await extract_intent(request.query)
        ranked = await rank_listings(request.query, intent, MOCK_LISTINGS)
    except GeminiTimeoutError as exc:
        return JSONResponse(
            status_code=504,
            content={"error": "Gateway timeout", "detail": str(exc)},
        )
    except GeminiAPIError as exc:
        import traceback; traceback.print_exc()
        return JSONResponse(
            status_code=503,
            content={"error": "Service unavailable", "detail": str(exc)},
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=502,
            content={"error": "Bad gateway", "detail": str(exc)},
        )

    listing_map = {str(l["id"]): l for l in MOCK_LISTINGS}

    enriched = []
    for r in ranked:
        listing = listing_map.get(str(r.get("id", "")), {})
        enriched.append(RankedResult(
            **r,
            title=listing.get("title"),
            price=listing.get("price"),
        ))

    return NeedBoardResponse(
        extracted=ExtractedIntent(**intent),
        rankedResults=enriched,
    )
