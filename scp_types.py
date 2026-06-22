import numpy as np
from scipy.sparse import csr_matrix
from typing import List, Set, Tuple

class SCPInstance:
    def __init__(self, num_elements: int, num_sets: int, sets: List[Set[int]], costs: List[float] = None):
        """
        Initialize an SCP instance.
        :param num_elements: Number of elements to be covered (1 to m).
        :param num_sets: Number of sets available (1 to n).
        :param sets: A list of sets, where each set contains the indices of elements it covers.
        :param costs: A list of costs for each set. Defaults to 1.0 for all sets (unicost).
        """
        self.num_elements = num_elements
        self.num_sets = num_sets
        self.sets = sets
        self.costs = costs if costs is not None else [1.0] * num_sets
        
        # Build 0-indexed representation for sets for performance
        self.sets_0indexed = [set(e - 1 for e in s) for s in sets]
        
        # Build sparse matrix for efficiency
        # Rows: elements, Cols: sets
        # A[i, j] = 1 if set j covers element i
        row_indices = []
        col_indices = []
        for set_idx, covered_elements in enumerate(sets):
            for element in covered_elements:
                # Elements in OR-Library are 1-indexed, we'll use 0-indexing internally
                row_indices.append(element - 1)
                col_indices.append(set_idx)
        
        self.matrix = csr_matrix(
            (np.ones(len(row_indices), dtype=int), (row_indices, col_indices)),
            shape=(num_elements, num_sets)
        )
        
        # Precompute list of sets covering each element (0-indexed)
        # to avoid extremely slow SciPy matrix row slicing during search
        self.element_to_sets = [list(self.matrix[e].indices) for e in range(num_elements)]

    @classmethod
    def from_or_library(cls, file_path: str):
        """
        Parse an OR-Library SCP instance file.
        Format:
        num_elements num_sets
        cost_set_1 cost_set_2 ... cost_set_n
        num_covered_by_element_1
        list_of_sets_covering_element_1
        ...
        """
        with open(file_path, 'r') as f:
            lines = f.read().split()
            
        if not lines:
            raise ValueError("Empty file")
            
        it = iter(lines)
        num_elements = int(next(it))
        num_sets = int(next(it))
        
        costs = [float(next(it)) for _ in range(num_sets)]
        
        # In OR-Library format, the sets are defined by which elements they cover.
        # We need to build the 'sets' list (which sets cover which elements).
        sets_to_elements = [set() for _ in range(num_sets)]
        
        for element_idx in range(num_elements):
            num_covering_sets = int(next(it))
            for _ in range(num_covering_sets):
                set_idx = int(next(it)) - 1  # 1-indexed to 0-indexed
                sets_to_elements[set_idx].add(element_idx + 1) # Elements are 1-indexed
                
        return cls(num_elements, num_sets, sets_to_elements, costs)

    def to_or_library(self, file_path: str):
        """
        Write the SCP instance in OR-Library format to a file.
        """
        element_covering_sets = [[] for _ in range(self.num_elements)]
        for set_idx, covered_elements in enumerate(self.sets):
            for elem in covered_elements:
                element_covering_sets[elem - 1].append(set_idx + 1)
                
        with open(file_path, 'w') as f:
            f.write(f"{self.num_elements} {self.num_sets}\n")
            
            # Write costs
            costs_str = " ".join(str(c) for c in self.costs)
            f.write(costs_str + "\n")
            
            # For each element, write number of covering sets and the list of covering sets
            for elem_idx in range(self.num_elements):
                cov_sets = element_covering_sets[elem_idx]
                f.write(f"{len(cov_sets)}\n")
                cov_sets_str = " ".join(str(s) for s in cov_sets)
                f.write(cov_sets_str + "\n")

    def __str__(self):
        return f"SCPInstance(m={self.num_elements}, n={self.num_sets})"
