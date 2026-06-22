import numpy as np
from scp_types import SCPInstance
from typing import List, Set, Tuple

def greedy_scp(instance: SCPInstance) -> Tuple[List[int], float]:
    """
    Greedy approximation algorithm for Set Covering Problem.
    Returns a list of set indices and the total cost.
    """
    m, n = instance.num_elements, instance.num_sets
    uncovered_elements = set(range(m))
    selected_sets = []
    total_cost = 0.0
    
    set_contents = instance.sets_0indexed
    
    while uncovered_elements:
        best_set_idx = -1
        best_efficiency = -1.0
        
        for i in range(n):
            # Efficiency = number of new elements covered / cost
            newly_covered = len(set_contents[i].intersection(uncovered_elements))
            if newly_covered > 0:
                efficiency = newly_covered / instance.costs[i]
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_set_idx = i
        
        if best_set_idx == -1:
            # Should not happen if a solution exists
            break
            
        selected_sets.append(best_set_idx)
        total_cost += instance.costs[best_set_idx]
        uncovered_elements -= set_contents[best_set_idx]
        
    return selected_sets, total_cost

if __name__ == "__main__":
    from typing import Tuple
    # Simple test
    m = 5
    n = 3
    sets = [
        {1, 2, 3},
        {3, 4},
        {4, 5}
    ]
    costs = [1.0, 1.0, 1.0]
    instance = SCPInstance(m, n, sets, costs)
    
    selected, cost = greedy_scp(instance)
    print(f"Selected sets: {selected}")
    print(f"Total cost: {cost}")
