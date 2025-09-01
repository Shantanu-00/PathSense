import numpy as np
from typing import List, Optional
from .nn import nearest_neighbor, _path_cost

def two_opt(
    path: List[int],
    dist_mx: np.ndarray,
    start: Optional[int] = None,
    end: Optional[int] = None,
    return_to_start: bool = False,
    max_passes: int = 50
) -> List[int]:
    """
    2-opt optimization with support for fixed start/end points
    """
    if len(path) <= 3:
        return path
    
    best = path[:]
    improved = True
    passes = 0
    
    # Determine fixed positions based on constraints
    fixed_positions = set()
    if start is not None:
        fixed_positions.add(0)  # Start is fixed at position 0
    if end is not None and not return_to_start:
        fixed_positions.add(len(best) - 1)  # End is fixed at last position
    
    while improved and passes < max_passes:
        improved = False
        passes += 1
        
        for i in range(1, len(best) - 2):
            if i in fixed_positions:
                continue
                
            for k in range(i + 1, len(best) - 1):
                if k in fixed_positions:
                    continue
                
                # Don't break fixed segments
                if _would_break_fixed(best, i, k, fixed_positions):
                    continue
                
                new_route = _two_opt_swap(best, i, k)
                if _path_cost(new_route, dist_mx) < _path_cost(best, dist_mx):
                    best = new_route
                    improved = True
                    break
            
            if improved:
                break
    
    return best

def _would_break_fixed(path: List[int], i: int, k: int, fixed_positions: set) -> bool:
    """Check if a 2-opt swap would break fixed positions"""
    # Check if swap would move fixed positions
    for pos in fixed_positions:
        if pos >= i and pos <= k:
            return True
    return False

def _two_opt_swap(route: List[int], i: int, k: int) -> List[int]:
    """Perform 2-opt swap between positions i and k"""
    return route[:i] + route[i:k+1][::-1] + route[k+1:]

def two_opt_optimize(
    dist_mx: np.ndarray,
    start: Optional[int] = None,
    end: Optional[int] = None,
    return_to_start: bool = False,
    max_passes: int = 50
) -> List[int]:
    """
    Complete 2-opt optimization from scratch
    """
    # First get a good initial solution using NN
    if start is not None and end is not None:
        initial = nearest_neighbor(dist_mx, start, end, return_to_start)
    elif start is not None:
        initial = nearest_neighbor(dist_mx, start, None, return_to_start)
    elif end is not None:
        initial = nearest_neighbor(dist_mx, None, end, return_to_start)
    else:
        initial = nearest_neighbor(dist_mx, None, None, return_to_start)
    
    # Apply 2-opt optimization
    return two_opt(initial, dist_mx, start, end, return_to_start, max_passes)