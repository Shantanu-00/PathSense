import numpy as np
import random
from typing import List, Optional, Set
from .nn import _path_cost

def genetic_tsp(
    dist_mx: np.ndarray,
    start: Optional[int] = None,
    end: Optional[int] = None,
    return_to_start: bool = False,
    pop_size: int = 100,
    generations: int = 500,
    mutation_rate: float = 0.2,
    elite_frac: float = 0.1
) -> List[int]:
    """
    Genetic algorithm for TSP with fixed start/end support
    """
    n = dist_mx.shape[0]
    if n == 0:
        return []
    if n == 1:
        return [0]
    
    # Initialize population based on constraints
    population = _initialize_population(n, start, end, return_to_start, pop_size)
    elite_count = max(1, int(elite_frac * pop_size))
    
    for generation in range(generations):
        # Evaluate fitness
        population.sort(key=lambda ind: _fitness(ind, dist_mx))
        elites = population[:elite_count]
        new_population = elites[:]
        
        # Breed new population
        while len(new_population) < pop_size:
            parent1, parent2 = _select_parents(population, dist_mx)
            child = _crossover(parent1, parent2, start, end, return_to_start)
            
            if random.random() < mutation_rate:
                child = _mutate(child, start, end, return_to_start)
            
            new_population.append(child)
        
        population = new_population
    
    # Return best individual
    population.sort(key=lambda ind: _fitness(ind, dist_mx))
    return population[0]

def _initialize_population(n: int, start: Optional[int], end: Optional[int], 
                         return_to_start: bool, pop_size: int) -> List[List[int]]:
    """Initialize population based on constraints"""
    population = []
    
    for _ in range(pop_size):
        if start is not None and end is not None:
            # Fixed start and end
            individual = [start]
            middle = [i for i in range(n) if i != start and i != end]
            random.shuffle(middle)
            individual.extend(middle)
            individual.append(end)
            
            if return_to_start and start != end:
                individual.append(start)
                
        elif start is not None:
            # Fixed start only
            individual = [start]
            others = [i for i in range(n) if i != start]
            random.shuffle(others)
            individual.extend(others)
            
            if return_to_start:
                individual.append(start)
                
        elif end is not None:
            # Fixed end only
            others = [i for i in range(n) if i != end]
            random.shuffle(others)
            individual = others + [end]
            
            if return_to_start:
                # Find best place to return from end
                individual.append(individual[0])
                
        else:
            # No fixed points
            individual = list(range(n))
            random.shuffle(individual)
            
            if return_to_start:
                individual.append(individual[0])
        
        population.append(individual)
    
    return population

def _fitness(individual: List[int], dist_mx: np.ndarray) -> float:
    """Calculate fitness (lower is better)"""
    return _path_cost(individual, dist_mx)

def _select_parents(population: List[List[int]], dist_mx: np.ndarray) -> tuple:
    """Tournament selection"""
    tournament_size = 3
    tournament = random.sample(population, tournament_size)
    tournament.sort(key=lambda ind: _fitness(ind, dist_mx))
    return tournament[0], tournament[1]

def _crossover(parent1: List[int], parent2: List[int], 
              start: Optional[int], end: Optional[int], 
              return_to_start: bool) -> List[int]:
    """Ordered crossover with constraint preservation"""
    n = len(parent1)
    child = [None] * n
    
    # Preserve fixed positions
    fixed_positions = {}
    if start is not None:
        fixed_positions[0] = start
    if end is not None and not return_to_start:
        fixed_positions[n-1] = end
    elif return_to_start and start is not None:
        fixed_positions[n-1] = start
    
    for pos, value in fixed_positions.items():
        child[pos] = value
    
    # Ordered crossover for non-fixed positions
    non_fixed_indices = [i for i in range(n) if child[i] is None]
    
    if non_fixed_indices:
        start_idx = min(non_fixed_indices)
        end_idx = max(non_fixed_indices)
        
        # Select random segment from parent1
        segment_start = random.randint(start_idx, end_idx)
        segment_end = random.randint(segment_start, end_idx)
        
        # Copy segment to child
        for i in range(segment_start, segment_end + 1):
            child[i] = parent1[i]
        
        # Fill remaining positions from parent2
        parent2_ptr = 0
        for i in range(start_idx, end_idx + 1):
            if child[i] is None:
                while parent2[parent2_ptr] in child or parent2[parent2_ptr] in fixed_positions.values():
                    parent2_ptr += 1
                child[i] = parent2[parent2_ptr]
                parent2_ptr += 1
    
    return child

def _mutate(individual: List[int], start: Optional[int], 
           end: Optional[int], return_to_start: bool) -> List[int]:
    """Swap mutation that preserves constraints"""
    n = len(individual)
    mutated = individual[:]
    
    # Identify mutable positions (not fixed)
    fixed_positions = set()
    if start is not None:
        fixed_positions.add(0)
    if end is not None and not return_to_start:
        fixed_positions.add(n-1)
    elif return_to_start and start is not None:
        fixed_positions.add(n-1)
    
    mutable_indices = [i for i in range(n) if i not in fixed_positions]
    
    if len(mutable_indices) >= 2:
        i, j = random.sample(mutable_indices, 2)
        mutated[i], mutated[j] = mutated[j], mutated[i]
    
    return mutated