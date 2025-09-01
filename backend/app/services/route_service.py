from typing import List, Tuple
import numpy as np
from app.schemas.places import Place
from app.schemas.routes import OptimizedRoute, RouteStep
from app.modules.optimization.nn import nearest_neighbor
from app.modules.optimization.two_opt import two_opt_optimize
from app.modules.optimization.genetic import genetic_tsp


class RouteService:
    @staticmethod
    def optimize(
        places: List[Place],
        distances: List[List[float]],
        durations: List[List[float]],
        algo: str = "nn2opt",
        return_to_start: bool = True,
        start_index: int = None,
        end_index: int = None
    ) -> OptimizedRoute:

        # Handle trivial cases
        if len(places) <= 1:
            return OptimizedRoute(
                optimized_places=places,
                visiting_order=list(range(len(places))),
                steps=[],
                total_distance=0,
                total_time=0
            )

        dist_mx = np.array(distances, dtype=float)
        dur_mx = np.array(durations, dtype=float)
        RouteService._validate_matrix(dist_mx, dur_mx)

        # Select optimization strategy
        if start_index is not None and end_index is not None:
            order = RouteService._optimize_with_fixed_points(dist_mx, start_index, end_index, algo, return_to_start)
        elif start_index is not None:
            order = RouteService._optimize_with_fixed_start(dist_mx, start_index, algo, return_to_start)
        elif end_index is not None:
            order = RouteService._optimize_with_fixed_end(dist_mx, end_index, algo, return_to_start)
        else:
            order = RouteService._optimize_free_start_end(dist_mx, algo, return_to_start)

        optimized_places = [places[i] for i in order]
        steps, total_dist, total_time = RouteService._build_steps(order, places, dist_mx, dur_mx)

        return OptimizedRoute(
            optimized_places=optimized_places,
            visiting_order=order,
            steps=steps,
            total_distance=int(total_dist),
            total_time=int(total_time),
        )

    # ---------------- OPTIMIZATION METHODS ---------------- #

    @staticmethod
    def _optimize_with_fixed_points(dist_mx: np.ndarray, start_idx: int, end_idx: int, algo: str, return_to_start: bool) -> List[int]:
        """Optimize with both start and end points fixed"""
        if algo == "nn":
            return nearest_neighbor(dist_mx, start_idx, end_idx, return_to_start)
        elif algo == "nn2opt":
            return two_opt_optimize(dist_mx, start_idx, end_idx, return_to_start)
        elif algo == "ga":
            return genetic_tsp(dist_mx, start_idx, end_idx, return_to_start)

    @staticmethod
    def _optimize_with_fixed_start(dist_mx: np.ndarray, start_idx: int, algo: str, return_to_start: bool) -> List[int]:
        """Optimize with fixed start point only"""
        if algo == "nn":
            return nearest_neighbor(dist_mx, start_idx, None, return_to_start)
        elif algo == "nn2opt":
            return two_opt_optimize(dist_mx, start_idx, None, return_to_start)
        elif algo == "ga":
            return genetic_tsp(dist_mx, start_idx, None, return_to_start)

    @staticmethod
    def _optimize_with_fixed_end(dist_mx: np.ndarray, end_idx: int, algo: str, return_to_start: bool) -> List[int]:
        """Optimize with fixed end point only"""
        if algo == "nn":
            return nearest_neighbor(dist_mx, None, end_idx, return_to_start)
        elif algo == "nn2opt":
            return two_opt_optimize(dist_mx, None, end_idx, return_to_start)
        elif algo == "ga":
            return genetic_tsp(dist_mx, None, end_idx, return_to_start)

    @staticmethod
    def _optimize_free_start_end(dist_mx: np.ndarray, algo: str, return_to_start: bool) -> List[int]:
        """Optimize without fixed points"""
        if algo == "nn":
            return nearest_neighbor(dist_mx, None, None, return_to_start)
        elif algo == "nn2opt":
            return two_opt_optimize(dist_mx, None, None, return_to_start)
        elif algo == "ga":
            return genetic_tsp(dist_mx, None, None, return_to_start)

    # ---------------- HELPERS ---------------- #

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
