import requests
from app.schemas.places import Place
from typing import List, Tuple


class OSRMExternalClient:
    BASE_URL = "https://router.project-osrm.org"

    @staticmethod
    def get_matrix(places: List[Place]) -> Tuple[List[List[float]], List[List[float]]]:
        if not places or len(places) < 2:
            raise ValueError("Need at least 2 places for matrix request")

        coords = ";".join([f"{p.longitude},{p.latitude}" for p in places])
        url = f"{OSRMExternalClient.BASE_URL}/table/v1/driving/{coords}?annotations=distance,duration"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data["distances"], data["durations"]
        except requests.RequestException as e:
            raise RuntimeError(f"External OSRM request failed: {e}")
