from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.places import Place
from app.schemas.routes import OptimizedRoute
from app.services.distance_service import DistanceService
from app.services.route_service import RouteService
from app.utils.session import get_session
from app.config.logging import logger

router = APIRouter(prefix="/route", tags=["Route"])

@router.post("/optimize", response_model=OptimizedRoute)
def optimize_route(
    session_id: str = Query(...),
    algo: str = Query("nn2opt"),
    return_to_start: bool = Query(True)
):
    """
    Optimize route for the user's confirmed places in session.
    Uses start and end points if available.
    """
    try:
        session_id, state = get_session(session_id)
        route = state.get("route", {})
        places: List[Place] = route.get("places", [])
        start: Optional[Place] = route.get("start")
        end: Optional[Place] = route.get("end")

        if not places and not start and not end:
            raise HTTPException(status_code=400, detail="No places to optimize.")

        # Build the list of places to optimize (only regular places)
        places_to_optimize = places.copy()
        
        logger.info(f"[Session: {session_id}] Optimizing {len(places_to_optimize)} regular places")
        logger.info(f"Start: {start.name if start else 'None'}, End: {end.name if end else 'None'}, Return to start: {return_to_start}")

        # Get distance matrix for all points (start + regular places + end)
        all_points = []
        if start:
            all_points.append(start)
        all_points.extend(places_to_optimize)
        if end and end != start:
            all_points.append(end)

        distances, durations = DistanceService.get_matrix(all_points, session_id=session_id)

        # Calculate indices for optimization
        start_idx = 0 if start else None
        end_idx = len(all_points) - 1 if end and end != start else None
        
        # If return_to_start is True, we need to end at the start point
        if return_to_start and start:
            end_idx = 0  # End at start point

        optimized = RouteService.optimize(
            places=all_points,
            distances=distances,
            durations=durations,
            algo=algo,
            return_to_start=return_to_start,
            start_index=start_idx,
            end_index=end_idx
        )

        logger.info(f"[Session: {session_id}] Optimized route with {len(optimized.optimized_places)} places using {algo}")
        return optimized

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Session: {session_id}] Failed to optimize route: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize route: {str(e)}")