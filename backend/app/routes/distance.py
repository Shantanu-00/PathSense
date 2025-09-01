from fastapi import APIRouter
from typing import List
from app.schemas.places import Place
from app.services.distance_service import DistanceService

router = APIRouter(prefix="/distance", tags=["Distance"])

@router.post("/matrix")
def get_distance_matrix(places: List[Place]) -> dict:
    distances, durations = DistanceService.get_matrix(places)
    return {"distances": distances, "durations": durations}
