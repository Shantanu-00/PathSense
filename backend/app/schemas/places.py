from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

class Place(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))  # Auto-generate ID if not provided
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    type: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "uuid-or-hash",
                "name": "Apollo Pharmacy",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "address": "FC Road, Pune",
                "type": "pharmacy"
            }
        }
        
class PlacesResponse(BaseModel):
    places: List[Place]
    count: int
    location: str
    business_type: str
    start: Optional[Place] = None
    end: Optional[Place] = None
