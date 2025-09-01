from pydantic import BaseModel
from typing import Optional, List
from app.schemas.places import Place

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    places: Optional[List[Place]] = None
    start: Optional[Place] = None  # ADDED
    end: Optional[Place] = None    # ADDED
    session_id: str