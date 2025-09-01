from fastapi import APIRouter, HTTPException
from app.modules.place_finder.osm_client import OSMClient

router = APIRouter(tags=["geocode"])

@router.get("/geocode")
def geocode(address: str):
    result = OSMClient.geocode(address)
    if result:
        lat, lon = result
        return {"latitude": lat, "longitude": lon}
    raise HTTPException(404, "Location not found")