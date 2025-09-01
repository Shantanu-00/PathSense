import requests
import numpy as np
from typing import Tuple, List
from app.schemas.places import Place


class DistanceCalculator:
    """
    Handles ONLY distance and duration calculations using OSRM.
    Returns raw matrices without any optimization.
    """

    OSRM_BASE_URL = "http://router.project-osrm.org"

    @staticmethod
    def calculate_distance_matrix(places: List[Place]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate distance and duration matrices between all places.

        Args:
            places: List of Place objects with coordinates

        Returns:
            Tuple of (distance_matrix, duration_matrix)
        """
        n = len(places)
        if n < 2:
            return np.zeros((n, n)), np.zeros((n, n))

        # Prepare coordinates for OSRM
        coordinates = ";".join([f"{p.longitude},{p.latitude}" for p in places])
        url = f"{DistanceCalculator.OSRM_BASE_URL}/table/v1/driving/{coordinates}?annotations=distance,duration"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"OSRM request failed: {e}")

        data = response.json()

        if "distances" not in data or "durations" not in data:
            raise ValueError("OSRM response missing 'distances' or 'durations'")

        distance_matrix = np.array(data["distances"], dtype=float)
        duration_matrix = np.array(data["durations"], dtype=float)

        return distance_matrix, duration_matrix

    @staticmethod
    def format_matrices_for_humans(
        distance_matrix: np.ndarray, duration_matrix: np.ndarray
    ) -> Tuple[List[List[str]], List[List[str]]]:
        """Convert raw matrices into human-readable strings (debugging only)."""
        n = distance_matrix.shape[0]
        human_distances, human_durations = [], []

        for i in range(n):
            dist_row, time_row = [], []
            for j in range(n):
                # Distance: meters → km
                dist_km = round(distance_matrix[i][j] / 1000, 2)
                dist_row.append(f"{dist_km} km" if dist_km else "0 km")

                # Duration: seconds → min
                time_min = round(duration_matrix[i][j] / 60, 2)
                time_row.append(f"{time_min} min" if time_min else "0 min")

            human_distances.append(dist_row)
            human_durations.append(time_row)

        return human_distances, human_durations
