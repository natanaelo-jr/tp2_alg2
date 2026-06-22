import numpy as np
from scp_types import SCPInstance
from typing import List, Set, Union
from collections import defaultdict

def get_sum_degree_bound(instance: SCPInstance, uncovered_elements: Set[int], available_sets: Union[List[int], Set[int]]) -> float:
    """
    Calculates the Sum-Degree (Efficiency) Lower Bound as described in Bläsius et al. (2022).
    L_eff = ceil( sum_{e in F} min_{v in e} (cost(v) / deg(v)) )
    """
    if not uncovered_elements:
        return 0.0
    
    available_set_set = available_sets if isinstance(available_sets, set) else set(available_sets)
    
    # Efficiently calculate current degrees of available sets for uncovered elements
    set_degrees = defaultdict(int)
    for element in uncovered_elements:
        for s_idx in instance.element_to_sets[element]:
            if s_idx in available_set_set:
                set_degrees[s_idx] += 1
                
    lower_bound = 0.0
    for element in uncovered_elements:
        min_ratio = float('inf')
        covering_sets = instance.element_to_sets[element]
        for s_idx in covering_sets:
            if s_idx in available_set_set:
                deg = set_degrees[s_idx]
                if deg > 0:
                    ratio = instance.costs[s_idx] / deg
                    if ratio < min_ratio:
                        min_ratio = ratio
        
        if min_ratio < float('inf'):
            lower_bound += min_ratio
            
    is_unicost = all(c == 1.0 for c in instance.costs)
    if is_unicost:
        return float(np.ceil(lower_bound))
    return lower_bound

def get_packing_bound(instance: SCPInstance, uncovered_elements: Set[int], available_sets: Union[List[int], Set[int]]) -> float:
    """
    Calculates the Disjoint-Subset (Packing) Lower Bound.
    """
    if not uncovered_elements:
        return 0.0
        
    available_set_set = available_sets if isinstance(available_sets, set) else set(available_sets)
    
    element_difficulty = []
    for element in uncovered_elements:
        covering_sets = [s for s in instance.element_to_sets[element] if s in available_set_set]
        if not covering_sets:
            continue
        min_cost = min(instance.costs[s] for s in covering_sets)
        element_difficulty.append((len(covering_sets), min_cost, element, covering_sets))
    
    element_difficulty.sort()
    
    packing_cost = 0.0
    used_sets = set()
    
    for _, min_cost, element, covering_sets in element_difficulty:
        if not any(s in used_sets for s in covering_sets):
            packing_cost += min_cost
            used_sets.update(covering_sets)
            
    return packing_cost
