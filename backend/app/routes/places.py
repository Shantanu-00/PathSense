from fastapi import APIRouter, HTTPException, Query, Body
from app.services.places_service import PlacesServices
from app.schemas.places import PlacesResponse, Place
from app.utils.session import get_session, store_in_session
from app.config.logging import logger
from typing import List, Optional
import uuid

router = APIRouter(tags=["places"])

# -------------------------------
# GET: fetch places
# -------------------------------
@router.get("/get-places", response_model=PlacesResponse)
async def get_places(
    business_type: str | None = Query(None),
    location: str | None = Query(None),
    count: int = Query(5),
    session_id: str | None = Query(None)
):
    try:
        session_id, state = get_session(session_id)

        business_type = business_type or state.get("intent", {}).get("business_type", "restaurant")
        location = location or state.get("intent", {}).get("location", "Pune")
        count = min(count, 10)

        response = await PlacesServices.get_places(business_type, location, count, session_id=session_id)
        if response.count == 0:
            logger.warning(f"No results for {business_type} in {location}")
        return response

    except Exception as e:
        logger.error(f"Failed to fetch places: {str(e)}")
        raise HTTPException(500, detail=f"Failed to fetch places: {str(e)}")

# -------------------------------
# GET: find places
# -------------------------------
@router.get("/find-places", response_model=PlacesResponse)
async def find_more_places(
    business_type: str = Query(...),
    location: str = Query(...),
    count: int = Query(5),
    session_id: str = Query(...)
):
    try:
        session_id, state = get_session(session_id)
        route = state.setdefault("route", {"places": [], "start": None, "end": None, "last_query": {}})

        # ✅ Normalize business type (convert to singular)
        normalized_business_type = business_type.rstrip('s')  # Remove trailing 's'
        if normalized_business_type == "":  # Handle edge case
            normalized_business_type = business_type

        # Fetch new places with normalized type
        all_results = await PlacesServices.get_places(normalized_business_type, location, count * 2, session_id=session_id)

        # ✅ Better deduplication: use ID if available, otherwise coordinates
        existing_places = route["places"]
        new_places = []
        
        for potential_place in all_results.places:
            # Check if place already exists by ID (if available)
            if hasattr(potential_place, 'id') and potential_place.id:
                if any(p.id == potential_place.id for p in existing_places if hasattr(p, 'id')):
                    continue
            
            # Check if place exists by coordinates (with some tolerance)
            coord_exists = any(
                abs(p.latitude - potential_place.latitude) < 0.0001 and 
                abs(p.longitude - potential_place.longitude) < 0.0001
                for p in existing_places
            )
            
            if not coord_exists:
                new_places.append(potential_place)

        # Limit to requested count
        final_places = new_places[:count]

        # ✅ Add to session
        route["places"].extend(final_places)
        route["last_query"] = {
            "business_type": business_type,
            "location": location
        }
        store_in_session(session_id, state)

        logger.info(f"[Session: {session_id}] Found {len(final_places)} new places for {business_type} in {location}. Total places now: {len(route['places'])}")

        # ✅ Return ALL places in the session, not just the new ones
        return PlacesResponse(
            places=route["places"],  # Return all places in session
            count=len(final_places),  # But count only the new ones
            location=location,
            business_type=business_type,
            start=route.get("start"),
            end=route.get("end")
        )
        
    except Exception as e:
        logger.error(f"Failed to find new places: {str(e)}")
        raise HTTPException(500, detail=f"Failed to find new places: {str(e)}")
# -------------------------------
# POST: confirm full list of places
# -------------------------------
@router.post("/confirm-places", response_model=PlacesResponse)
async def confirm_places(
    session_id: str | None = Query(None),
    request: dict = Body(...)
):
    try:
        session_id, state = get_session(session_id)
        route = state.setdefault('route', {"places": [], "start": None, "end": None, "last_query": {}})

        # Extract places from request body
        places_data = request.get("places", [])
        places = [Place(**place) for place in places_data]
        
        # Handle start/end if provided
        start_data = request.get("start")
        end_data = request.get("end")
        
        if start_data:
          route['start'] = Place(**start_data)
        if end_data:
            route['end'] = Place(**end_data)
        
        # Update places
        route['places'] = places
        
        store_in_session(session_id, state)
        logger.info(f"[Session: {session_id}] Confirmed {len(places)} places with start/end points")

        return PlacesResponse(
            places=places,
            count=len(places),
            location=route.get('last_query', {}).get('location', "Unknown"),
            business_type=route.get('last_query', {}).get('business_type', "Unknown"),
            start=route.get('start'),
            end=route.get('end')
        )
    except Exception as e:
        logger.error(f"Failed to confirm places: {str(e)}")
        raise HTTPException(500, detail=f"Failed to confirm places: {str(e)}")

# -------------------------------
# POST: add a single place
# -------------------------------
@router.post("/add-place", response_model=PlacesResponse)
async def add_place(
    session_id: str | None = Query(None), 
    place: Place = Body(...)
):
    try:
        session_id, state = get_session(session_id)
        route = state.setdefault('route', {"places": [], "start": None, "end": None, "last_query": {}})
        
        # Get current places before adding
        current_places = route.get('places', [])
        
        # Add the new place (with duplicate check)
        existing_coords = {(p.latitude, p.longitude) for p in current_places}
        if (place.latitude, place.longitude) in existing_coords:
            raise HTTPException(400, detail="Place already exists")
            
        if not getattr(place, "id", None):
            setattr(place, "id", str(uuid.uuid4()))
        current_places.append(place)
        route['places'] = current_places
        
        store_in_session(session_id, state)
        logger.info(f"[Session: {session_id}] Added place {place.name}. Total places: {len(current_places)}")

        return PlacesResponse(
            places=current_places,
            count=len(current_places),
            location=route.get('last_query', {}).get('location', "Unknown"),
            business_type=route.get('last_query', {}).get('business_type', "Unknown"),
            start=route.get('start'),
            end=route.get('end')
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add place: {str(e)}")
        raise HTTPException(500, detail=f"Failed to add place: {str(e)}")

# -------------------------------
# POST: remove a place
# -------------------------------
@router.post("/remove-place", response_model=PlacesResponse)
async def remove_place(
    session_id: str | None = Query(None), 
    request: dict = Body(...)
):
    try:
        session_id, state = get_session(session_id)
        route = state.setdefault('route', {"places": [], "start": None, "end": None, "last_query": {}})
        
        place_id = request.get("place_id")
        if not place_id:
            raise HTTPException(status_code=400, detail="Missing place_id")
            
        # Get current places and remove the specified one
        # Get current places and remove the specified one
        current_places = route.get('places', [])
        updated_places = [p for p in current_places if getattr(p, "id", None) != place_id]
        route['places'] = updated_places

        # Clear start/end if the removed place was one of them
        if route.get("start") and getattr(route["start"], "id", None) == place_id:
            route["start"] = None
        if route.get("end") and getattr(route["end"], "id", None) == place_id:
            route["end"] = None
        
        store_in_session(session_id, state)
        logger.info(f"[Session: {session_id}] Removed place {place_id}. Remaining places: {len(updated_places)}")

        return PlacesResponse(
            places=updated_places,
            count=len(updated_places),
            location=route.get('last_query', {}).get('location', "Unknown"),
            business_type=route.get('last_query', {}).get('business_type', "Unknown"),
            start=route.get('start'),
            end=route.get('end')
        )
    except Exception as e:
        logger.error(f"Failed to remove place: {str(e)}")
        raise HTTPException(500, detail=f"Failed to remove place: {str(e)}")

# -------------------------------
# POST: set start/end points
# -------------------------------
@router.post("/set-start-end", response_model=PlacesResponse)
async def set_start_end(
    session_id: str | None = Query(None),
    start: Optional[Place] = Body(None),
    end: Optional[Place] = Body(None)
):
    try:
        session_id, state = get_session(session_id)
        
        # Get current places before updating start/end
        route = state.setdefault('route', {"places": [], "start": None, "end": None, "last_query": {}})
        current_places = route.get('places', [])
        
        # Update start/end points
        if start:
            if not getattr(start, "id", None):
                setattr(start, "id", str(uuid.uuid4()))
            route['start'] = start
        if end:
            if not getattr(end, "id", None):
                setattr(end, "id", str(uuid.uuid4()))
            route['end'] = end
        
        store_in_session(session_id, state)
        logger.info(f"[Session: {session_id}] Updated start/end points. Current places: {len(current_places)}")

        # Return the current places along with start/end info
        return PlacesResponse(
            places=current_places,
            count=len(current_places),
            location=route.get('last_query', {}).get('location', "Unknown"),
            business_type=route.get('last_query', {}).get('business_type', "Unknown"),
            start=route.get('start'),
            end=route.get('end')
        )
    except Exception as e:
        logger.error(f"Failed to set start/end points: {str(e)}")
        raise HTTPException(500, detail=f"Failed to set start/end points: {str(e)}")
    

    # -------------------------------
# POST: reset start or end point
# -------------------------------
@router.post("/reset-start-end", response_model=PlacesResponse)
async def reset_start_end(
    session_id: str | None = Query(None),
    request: dict = Body(...)
):
    """
    Reset a place from being start or end.
    Adds it back to the regular places list if not already there.
    """
    try:
        session_id, state = get_session(session_id)
        route = state.setdefault('route', {"places": [], "start": None, "end": None, "last_query": {}})

        reset_start = request.get("reset_start", False)
        reset_end = request.get("reset_end", False)

        current_places = route.get('places', [])

        # Reset start
        if reset_start and route.get("start"):
            start_place = route["start"]
            route["start"] = None
            # add to places if not already there
            if not any(p.id == start_place.id for p in current_places):
                current_places.append(start_place)

        # Reset end
        if reset_end and route.get("end"):
            end_place = route["end"]
            route["end"] = None
            # add to places if not already there
            if not any(p.id == end_place.id for p in current_places):
                current_places.append(end_place)

        route['places'] = current_places
        store_in_session(session_id, state)

        logger.info(f"[Session: {session_id}] Reset start/end points")

        return PlacesResponse(
            places=current_places,
            count=len(current_places),
            location=route.get('last_query', {}).get('location', "Unknown"),
            business_type=route.get('last_query', {}).get('business_type', "Unknown"),
            start=route.get('start'),
            end=route.get('end')
        )

    except Exception as e:
        logger.error(f"Failed to reset start/end: {str(e)}")
        raise HTTPException(500, detail=f"Failed to reset start/end: {str(e)}")
