from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service  # Correct import
from app.config.logging import logger

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        return await chat_service.handle_chat(request.query, request.session_id)  # Correct method: handle_chat
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(500, detail=str(e))