import numpy as np
from typing import List, Tuple
from ortools.constraint_solver import routing_enums_pb2, pywrapcp


class RouteOptimizer:
    """
    Handles ONLY route optimization using TSP.
    Takes distance matrix and returns optimal route.
    """

    @staticmethod
    def solve_tsp(distance_matrix: np.ndarray) -> Tuple[List[int], float]:
        """
        Solve TSP for optimal route.

        Args:
            distance_matrix: N x N numpy array of distances

        Returns:
            Tuple (optimal_order, total_distance_meters)
        """
        if distance_matrix.size == 0:
            return [], 0.0

        # Routing manager
        manager = pywrapcp.RoutingIndexManager(
            distance_matrix.shape[0],  # number of locations
            1,                         # number of vehicles
            0                          # depot (start/end point)
        )
        routing = pywrapcp.RoutingModel(manager)

        # Distance callback
        def distance_callback(from_index, to_index):
            return int(distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)])

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Search params
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

        # Solve
        solution = routing.SolveWithParameters(search_params)

        if not solution:
            return list(range(len(distance_matrix))), float(np.sum(distance_matrix))

        return RouteOptimizer._extract_solution(manager, routing, solution, distance_matrix)

    @staticmethod
    def _extract_solution(manager, routing, solution, distance_matrix: np.ndarray) -> Tuple[List[int], float]:
        """Extract route and distance from OR-Tools solution."""
        index = routing.Start(0)
        route, total_distance = [], 0

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            prev_index = index
            index = solution.Value(routing.NextVar(index))
            total_distance += routing.GetArcCostForVehicle(prev_index, index, 0)

        route.append(manager.IndexToNode(index))
        return route, total_distance

    @staticmethod
    def optimize_route_with_durations(
        optimal_route: List[int],
        distance_matrix: np.ndarray,
        duration_matrix: np.ndarray,
    ) -> List[Tuple[int, float, float]]:
        """
        Get segment-level details for optimized route.

        Returns:
            List of tuples (to_node_index, distance_km, duration_min)
        """
        route_details = []
        for i in range(len(optimal_route) - 1):
            from_idx, to_idx = optimal_route[i], optimal_route[i + 1]
            distance_km = round(distance_matrix[from_idx][to_idx] / 1000, 2)
            duration_min = round(duration_matrix[from_idx][to_idx] / 60, 2)
            route_details.append((to_idx, distance_km, duration_min))

        return route_details
