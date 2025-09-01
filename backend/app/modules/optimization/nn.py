import numpy as np
from typing import List, Optional

def nearest_neighbor(
    dist_mx: np.ndarray,
    start: Optional[int] = None,
    end: Optional[int] = None,
    return_to_start: bool = False
) -> List[int]:
    n = dist_mx.shape[0]
    
    # Handle different optimization scenarios
    if start is not None and end is not None:
        # Fixed start and end points
        return _nn_fixed_start_end(dist_mx, start, end)
    elif start is not None:
        # Fixed start point only
        return _nn_fixed_start(dist_mx, start, return_to_start)
    elif end is not None:
        # Fixed end point only
        return _nn_fixed_end(dist_mx, end, return_to_start)
    else:
        # No fixed points - find optimal start/end
        return _nn_free_start_end(dist_mx, return_to_start)

def _nn_fixed_start_end(dist_mx: np.ndarray, start: int, end: int) -> List[int]:
    """Fixed start and end points"""
    n = dist_mx.shape[0]
    if n <= 2:
        return [start, end] if start != end else [start]
    
    unvisited = set(range(n)) - {start, end}
    path = [start]
    current = start
    
    while unvisited:
        next_node = min(unvisited, key=lambda j: dist_mx[current][j])
        path.append(next_node)
        unvisited.remove(next_node)
        current = next_node
    
    path.append(end)
    return path

def _nn_fixed_start(dist_mx: np.ndarray, start: int, return_to_start: bool) -> List[int]:
    """Fixed start point only"""
    n = dist_mx.shape[0]
    if n == 1:
        return [start]
    
    unvisited = set(range(n)) - {start}
    path = [start]
    current = start
    
    while unvisited:
        next_node = min(unvisited, key=lambda j: dist_mx[current][j])
        path.append(next_node)
        unvisited.remove(next_node)
        current = next_node
    
    if return_to_start:
        path.append(start)
    
    return path

def _nn_fixed_end(dist_mx: np.ndarray, end: int, return_to_start: bool) -> List[int]:
    """Fixed end point only"""
    n = dist_mx.shape[0]
    if n == 1:
        return [end]
    
    # Try all possible starting points and choose the best
    best_path = None
    best_cost = float('inf')
    
    for start in range(n):
        if start == end:
            continue
            
        path = [start]
        current = start
        unvisited = set(range(n)) - {start, end}
        
        while unvisited:
            next_node = min(unvisited, key=lambda j: dist_mx[current][j])
            path.append(next_node)
            unvisited.remove(next_node)
            current = next_node
        
        path.append(end)
        
        if return_to_start:
            # Find the best place to return to start from end
            cost = _path_cost(path, dist_mx) + dist_mx[end][start]
            if cost < best_cost:
                best_cost = cost
                best_path = path + [start]
        else:
            cost = _path_cost(path, dist_mx)
            if cost < best_cost:
                best_cost = cost
                best_path = path
    
    return best_path or [end]

def _nn_free_start_end(dist_mx: np.ndarray, return_to_start: bool) -> List[int]:
    """No fixed points - find optimal start/end"""
    n = dist_mx.shape[0]
    if n == 0:
        return []
    if n == 1:
        return [0]
    
    if return_to_start:
        # Traditional TSP - return to start
        return _nn_tsp(dist_mx)
    else:
        # Open TSP - find optimal start and end
        return _nn_open_tsp(dist_mx)

def _nn_tsp(dist_mx: np.ndarray) -> List[int]:
    """Traditional TSP with return to start"""
    n = dist_mx.shape[0]
    best_path = None
    best_cost = float('inf')
    
    for start in range(n):
        path = [start]
        current = start
        unvisited = set(range(n)) - {start}
        
        while unvisited:
            next_node = min(unvisited, key=lambda j: dist_mx[current][j])
            path.append(next_node)
            unvisited.remove(next_node)
            current = next_node
        
        path.append(start)  # Return to start
        cost = _path_cost(path, dist_mx)
        
        if cost < best_cost:
            best_cost = cost
            best_path = path
    
    return best_path or list(range(n))

def _nn_open_tsp(dist_mx: np.ndarray) -> List[int]:
    """Open TSP without return to start"""
    n = dist_mx.shape[0]
    best_path = None
    best_cost = float('inf')
    
    for start in range(n):
        path = [start]
        current = start
        unvisited = set(range(n)) - {start}
        
        while unvisited:
            next_node = min(unvisited, key=lambda j: dist_mx[current][j])
            path.append(next_node)
            unvisited.remove(next_node)
            current = next_node
        
        cost = _path_cost(path, dist_mx)
        
        if cost < best_cost:
            best_cost = cost
            best_path = path
    
    return best_path or list(range(n))

def _path_cost(path: List[int], dist_mx: np.ndarray) -> float:
    """Calculate total cost of a path"""
    return sum(dist_mx[path[i]][path[i+1]] for i in range(len(path)-1))