from typing import List, Tuple
import numpy as np
from app.schemas.places import Place
from app.schemas.routes import OptimizedRoute, RouteStep
from app.modules.optimization.nn import nearest_neighbor
from app.modules.optimization.two_opt import two_opt
from app.modules.optimization.genetic import genetic_tsp

class RouteServiceMatrix:
    """
    Optimize a route GIVEN distance/duration matrices (no OSRM call here).
    """

    @staticmethod
    def optimize_from_matrix(
        places: List[Place],
        distances: List[List[float]],
        durations: List[List[float]],
        algo: str = "nn2opt",
        return_to_start: bool = True,
    ) -> OptimizedRoute:

        dist_mx = np.array(distances, dtype=float)
        dur_mx  = np.array(durations, dtype=float)
        RouteServiceMatrix._validate_matrix(dist_mx, dur_mx)

        algo = algo.lower()
        if algo == "nn":
            order = nearest_neighbor(dist_mx, start=0, return_to_start=return_to_start)
        elif algo == "nn2opt":
            base  = nearest_neighbor(dist_mx, start=0, return_to_start=return_to_start)
            order = two_opt(base, dist_mx, return_to_start=return_to_start, max_passes=30)
        elif algo == "ga":
            order = genetic_tsp(dist_mx, return_to_start=return_to_start, pop_size=120, generations=350, mutation_rate=0.15, elite_frac=0.08)
        else:
            raise ValueError(f"Unknown algorithm '{algo}'")

        optimized_places = [places[i] for i in order]
        steps, total_dist, total_time = RouteServiceMatrix._build_steps(order, places, dist_mx, dur_mx)

        return OptimizedRoute(
            optimized_places=optimized_places,
            visiting_order=order,
            steps=steps,
            total_distance=int(total_dist),
            total_time=int(total_time),
        )

    @staticmethod
    def _build_steps(order: List[int], places: List[Place], dist_mx: np.ndarray, dur_mx: np.ndarray) -> Tuple[List[RouteStep], int, int]:
        steps: List[RouteStep] = []
        total_dist, total_time = 0, 0

        for i in range(len(order) - 1):
            a, b = order[i], order[i + 1]
            d = int(round(dist_mx[a][b]))
            t = int(round(dur_mx[a][b]))
            steps.append(RouteStep(
                from_place=places[a],
                to_place=places[b],
                distance_meters=d,
                duration_seconds=t
            ))
            total_dist += d
            total_time += t

        return steps, total_dist, total_time

    @staticmethod
    def _validate_matrix(dist_mx: np.ndarray, dur_mx: np.ndarray):
        if dist_mx.shape != dur_mx.shape or dist_mx.shape[0] != dist_mx.shape[1]:
            raise ValueError("Invalid matrix shape")
        if np.any(np.isnan(dist_mx)) or np.any(np.isnan(dur_mx)):
            raise ValueError("Matrix has NaN")
        if np.any(dist_mx < 0) or np.any(dur_mx < 0):
            raise ValueError("Matrix has negative values")
