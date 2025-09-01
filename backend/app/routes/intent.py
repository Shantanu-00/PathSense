from fastapi import APIRouter, HTTPException
from app.services.intent_extraction import intent_extraction_service
router = APIRouter(tags=["intent"])

@router.get("/extract-intent")
async def extract_intent(query:str):
    try:
        return intent_extraction_service.extract_intent(query)
    except Exception as e:
        raise HTTPException(500, detail= str(e))