# app/schemas/routes.py
from pydantic import BaseModel
from typing import List
from app.schemas.places import Place


class RouteStep(BaseModel):
    """Represents a single step in the route (from one place to another)."""
    from_place: Place
    to_place: Place
    distance_meters: int
    duration_seconds: int


class OptimizedRoute(BaseModel):
    """Represents the full optimized route with order, distance, and time."""
    optimized_places: List[Place]
    visiting_order: List[int]
    steps: List[RouteStep]
    total_distance: int   # meters
    total_time: int       # seconds

    class Config:
        json_schema_extra = {
            "example": {
                "optimized_places": [
                    {"name": "Place A", "latitude": 18.52, "longitude": 73.85},
                    {"name": "Place B", "latitude": 18.53, "longitude": 73.84},
                ],
                "visiting_order": [0, 1],
                "steps": [
                    {
                        "from_place": {"name": "Place A", "latitude": 18.52, "longitude": 73.85},
                        "to_place": {"name": "Place B", "latitude": 18.53, "longitude": 73.84},
                        "distance_meters": 1200,
                        "duration_seconds": 300
                    }
                ],
                "total_distance": 1200,
                "total_time": 300
            }
        }
