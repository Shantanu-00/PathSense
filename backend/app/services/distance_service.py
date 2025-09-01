from typing import List, Tuple
from app.schemas.places import Place
from app.modules.routing.osrm_client import OSRMClient
from app.modules.routing.osrm_public_client import OSRMExternalClient
from app.config.logging import logger


class DistanceService:
    """
    Provides distance/duration matrices from either:
    - Local Docker OSRM
    - Public API fallback
    """

    @staticmethod
    def get_matrix(places: List[Place], session_id: str = None) -> Tuple[List[List[float]], List[List[float]]]:
        if not places or len(places) < 2:
            raise ValueError("Need at least 2 places for distance matrix")

        try:
            # Try local docker OSRM
            distances, durations = OSRMClient.get_matrix(places)
            logger.info(f"[Session: {session_id}] Distance matrix computed via local OSRM for {len(places)} places")
        except Exception as e:
            logger.warning(f"[Session: {session_id}] Local OSRM failed: {e}. Falling back to external API.")
            distances, durations = OSRMExternalClient.get_matrix(places)

        # Validate matrix dimensions
        n = len(places)
        if len(distances) != n or any(len(row) != n for row in distances):
            raise ValueError("Distance matrix shape mismatch")
        if len(durations) != n or any(len(row) != n for row in durations):
            raise ValueError("Duration matrix shape mismatch")

        return distances, durations
