import heapq
import time
from typing import List, Set, Tuple, Optional
from scp_types import SCPInstance
from greedy import greedy_scp
from utils import get_sum_degree_bound, get_packing_bound

class BranchAndBoundSolver:
    def __init__(self, instance: SCPInstance, strategy: str = "dfs", lower_bound_type: str = "sum_degree", initial_ub_type: str = "greedy"):
        self.instance = instance
        self.strategy = strategy.lower()
        self.lower_bound_type = lower_bound_type.lower()
        self.initial_ub_type = initial_ub_type.lower()
        
        self.best_solution: List[int] = []
        self.best_cost: float = float('inf')
        self.nodes_explored = 0
        
        if self.initial_ub_type == "greedy":
            # Initial upper bound using greedy
            greedy_sol, greedy_cost = greedy_scp(instance)
            self.best_solution = greedy_sol
            self.best_cost = greedy_cost
        elif self.initial_ub_type == "trivial":
            # Trivial upper bound: select all sets
            self.best_solution = list(range(instance.num_sets))
            self.best_cost = sum(instance.costs)

    def _get_lower_bound(self, uncovered_elements: Set[int], available_sets: List[int]) -> float:
        if self.lower_bound_type == "sum_degree":
            return get_sum_degree_bound(self.instance, uncovered_elements, available_sets)
        elif self.lower_bound_type == "packing":
            return get_packing_bound(self.instance, uncovered_elements, available_sets)
        elif self.lower_bound_type == "both":
            # Surgical pruning: cheap one first
            lb = get_sum_degree_bound(self.instance, uncovered_elements, available_sets)
            if lb >= self.best_cost:
                return lb
            return max(lb, get_packing_bound(self.instance, uncovered_elements, available_sets))
        return 0.0

    def solve(self, timeout: float = 10800): # 3 hours default
        start_time = time.time()
        
        m = self.instance.num_elements
        initial_uncovered = set(range(m))
        initial_available = set(range(self.instance.num_sets))
        
        if self.strategy == "dfs":
            self._dfs(initial_uncovered, initial_available, [], 0.0, start_time, timeout)
        elif self.strategy == "best_first":
            self._best_first(initial_uncovered, initial_available, start_time, timeout)
            
        return self.best_solution, self.best_cost, self.nodes_explored

    def _dfs(self, uncovered, available, current_sol, current_cost, start_time, timeout):
        if time.time() - start_time > timeout:
            return
            
        self.nodes_explored += 1
        
        if not uncovered:
            if current_cost < self.best_cost:
                self.best_cost = current_cost
                self.best_solution = current_sol[:]
            return
            
        if not available:
            return
            
        # Lower bound pruning
        lb = self._get_lower_bound(uncovered, available)
        if current_cost + lb >= self.best_cost:
            return
            
        # Branching: Pick an element and try all sets covering it
        # Heuristic: Pick the element covered by the fewest available sets
        min_covering = float('inf')
        target_element = -1
        
        for e in uncovered:
            num_covering = len(available.intersection(self.instance.element_to_sets[e]))
            if num_covering < min_covering:
                min_covering = num_covering
                target_element = e
                if min_covering <= 1:
                    break
        
        if target_element == -1 or min_covering == 0:
            # Infeasible subproblem or element cannot be covered
            return
            
        covering_sets = [s for s in self.instance.element_to_sets[target_element] if s in available]
        
        # Sort covering sets by efficiency (greedy heuristic)
        covering_sets.sort(
            key=lambda s: len(uncovered.intersection(self.instance.sets_0indexed[s])) / self.instance.costs[s],
            reverse=True
        )

        # Mutually exclusive branching to eliminate search redundancy
        remaining_available = available.copy()
        for s_idx in covering_sets:
            # Branch where s_idx is selected.
            remaining_available.remove(s_idx)
            new_uncovered = uncovered - self.instance.sets_0indexed[s_idx]
            new_available = remaining_available.copy()
            self._dfs(new_uncovered, new_available, current_sol + [s_idx], current_cost + self.instance.costs[s_idx], start_time, timeout)

    def _best_first(self, uncovered, available, start_time, timeout):
        # Priority Queue: (lower_bound_estimate, counter, current_cost, uncovered, available, current_sol)
        lb = self._get_lower_bound(uncovered, available)
        counter = 0
        pq = [(lb, counter, 0.0, uncovered, available, [])]
        
        while pq and (time.time() - start_time < timeout):
            # Memory safety limit: cap priority queue at 50,000 nodes to prevent RAM explosion / thrashing.
            if len(pq) > 50000:
                break
                
            self.nodes_explored += 1
            est, _, current_cost, current_uncovered, current_available, current_sol = heapq.heappop(pq)
            
            # Use 'est' (lower bound estimate calculated when pushed) directly for pruning.
            if est >= self.best_cost:
                continue
                
            if not current_uncovered:
                if current_cost < self.best_cost:
                    self.best_cost = current_cost
                    self.best_solution = current_sol
                continue

            if not current_available:
                continue
                
            # Branching
            min_covering = float('inf')
            target_element = -1
            
            for e in current_uncovered:
                num_covering = len(current_available.intersection(self.instance.element_to_sets[e]))
                if num_covering < min_covering:
                    min_covering = num_covering
                    target_element = e
                    if min_covering <= 1:
                        break
            
            if target_element == -1 or min_covering == 0:
                continue
                
            covering_sets = [s for s in self.instance.element_to_sets[target_element] if s in current_available]
            covering_sets.sort(
                key=lambda s: len(current_uncovered.intersection(self.instance.sets_0indexed[s])) / self.instance.costs[s],
                reverse=True
            )
            
            # Mutually exclusive branching
            remaining_available = current_available.copy()
            for s_idx in covering_sets:
                remaining_available.remove(s_idx)
                new_uncovered = current_uncovered - self.instance.sets_0indexed[s_idx]
                new_available = remaining_available.copy()
                new_cost = current_cost + self.instance.costs[s_idx]
                
                if new_cost < self.best_cost:
                    lb = self._get_lower_bound(new_uncovered, new_available)
                    if new_cost + lb < self.best_cost:
                        counter += 1
                        heapq.heappush(pq, (new_cost + lb, counter, new_cost, new_uncovered, new_available, current_sol + [s_idx]))

if __name__ == "__main__":
    # Small test
    from scp_types import SCPInstance
    m = 5
    n = 3
    sets = [{1, 2, 3}, {3, 4}, {4, 5}]
    costs = [1.0, 1.0, 1.0]
    instance = SCPInstance(m, n, sets, costs)
    
    solver = BranchAndBoundSolver(instance, strategy="best_first", lower_bound_type="both")
    sol, cost, nodes = solver.solve()
    print(f"B&B Solution: {sol}, Cost: {cost}, Nodes: {nodes}")
