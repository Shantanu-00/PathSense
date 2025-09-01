from app.modules.place_finder.osm_client import OSMClient
from app.schemas.places import PlacesResponse, Place
from app.config.logging import logger
from typing import List, Optional
from app.utils.session import store_in_session, get_from_session
import uuid

class PlacesServices:
    @staticmethod
    async def get_places(
        business_type: str,
        location: str,
        count: int = 5,
        session_id: Optional[str] = None
    ) -> PlacesResponse:
        logger.info(f"[Session: {session_id}] Fetching {count} {business_type}(s) in {location}")

        session_data = get_from_session(session_id) if session_id else {}
        route = session_data.setdefault('route', {"places": [], "start": None, "end": None, "last_query": {}})

        business_types = [bt.strip().lower() for bt in business_type.split(',')]
        all_new_places: List[Place] = []

        for bt in business_types:
            logger.info(f"[Session: {session_id}] Searching OSM for: {bt}")
            
            # Get only NEW places that aren't already in session
            existing_coords = {(p.latitude, p.longitude) for p in route['places']}
            if route.get('start'):
                existing_coords.add((route['start'].latitude, route['start'].longitude))
            if route.get('end'):
                existing_coords.add((route['end'].latitude, route['end'].longitude))
            
            places = await OSMClient.search_places(bt, location, limit=count)
            
            # Filter out duplicates and limit to requested count
            unique_new_places = []
            for p in places:
                if (p.latitude, p.longitude) not in existing_coords:
                    if not getattr(p, "id", None):
                        setattr(p, "id", str(uuid.uuid4()))
                    unique_new_places.append(p)
                    existing_coords.add((p.latitude, p.longitude))
                
                if len(unique_new_places) >= count:
                    break
            
            all_new_places.extend(unique_new_places)

        # Add new places to session
        route['places'].extend(all_new_places)
        route['last_query'] = {"business_type": business_type, "location": location, "count": count}

        if session_id:
            session_data['route'] = route
            store_in_session(session_id, session_data)
            logger.info(f"[Session: {session_id}] Added {len(all_new_places)} new places, total now {len(route['places'])}")

        response = PlacesResponse(
            places=route['places'],
            count=len(route['places']),
            location=location.title(),
            business_type=business_type.lower(),
            start=route.get('start'),
            end=route.get('end')
        )

        return response

    @staticmethod
    def add_place(session_id: str, place: Place):
        session_data = get_from_session(session_id)
        route = session_data.setdefault('route', {"places": [], "start": None, "end": None, "last_query": {}})
        
        # Check for duplicates
        existing_coords = {(p.latitude, p.longitude) for p in route['places']}
        if (place.latitude, place.longitude) in existing_coords:
            return
            
        if not getattr(place, "id", None):
            setattr(place, "id", str(uuid.uuid4()))
        route['places'].append(place)
        store_in_session(session_id, session_data)
        logger.info(f"[Session: {session_id}] Added place {place.name}")

    @staticmethod
    def remove_place(session_id: str, place_id: str):
        session_data = get_from_session(session_id)
        route = session_data.get('route', {})
        if not route or 'places' not in route:
            return
        
        # Also check if this is a start/end point
        if route.get('start') and getattr(route['start'], 'id', None) == place_id:
            route['start'] = None
        if route.get('end') and getattr(route['end'], 'id', None) == place_id:
            route['end'] = None
            
        route['places'] = [p for p in route['places'] if getattr(p, "id", None) != place_id]
        store_in_session(session_id, session_data)
        logger.info(f"[Session: {session_id}] Removed place {place_id}")

    @staticmethod
    def set_start_end(session_id: str, start: Optional[Place] = None, end: Optional[Place] = None):
        session_data = get_from_session(session_id)
        route = session_data.setdefault('route', {"places": [], "start": None, "end": None, "last_query": {}})
        
        if start:
            if not getattr(start, "id", None):
                setattr(start, "id", str(uuid.uuid4()))
            route['start'] = start
        if end:
            if not getattr(end, "id", None):
                setattr(end, "id", str(uuid.uuid4()))
            route['end'] = end
            
        store_in_session(session_id, session_data)
        logger.info(f"[Session: {session_id}] Updated start/end points")