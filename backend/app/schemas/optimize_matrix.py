from pydantic import BaseModel, Field
from typing import List
from app.schemas.places import Place

class OptimizeMatrixRequest(BaseModel):
    places: List[Place] = Field(..., description="Order must match rows/cols of matrices")
    distances: List[List[float]]  # meters
    durations: List[List[float]]  # seconds

    class Config:
        json_schema_extra = {
            "example": {
                "places": [
                    {"name": "A", "latitude": 18.52, "longitude": 73.85},
                    {"name": "B", "latitude": 18.53, "longitude": 73.84},
                    {"name": "C", "latitude": 18.54, "longitude": 73.86}
                ],
                "distances": [[0, 1000, 2500],[1000,0,1400],[2400,1400,0]],
                "durations": [[0, 120, 300],[115,0,160],[290,150,0]]
            }
        }
