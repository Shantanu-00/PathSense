from pydantic import BaseModel
from typing import List, Optional
from app.schemas.intent import Intent
from app.schemas.places import Place

class SessionData(BaseModel):
    session_id: str
    intent: Intent
    candidate_places: List[Place] = []
    confirmed: bool = False
