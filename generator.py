import random
import numpy as np
from scp_types import SCPInstance
from typing import List, Set

def generate_uniform_instance(m: int, n: int, p: float) -> SCPInstance:
    """
    Generate a uniform random SCP instance.
    m: number of elements
    n: number of sets
    p: probability that an element is in a set
    """
    sets = []
    for _ in range(n):
        s = set()
        for i in range(1, m + 1):
            if random.random() < p:
                s.add(i)
        sets.append(s)
    
    # Ensure all elements are covered by at least one set
    uncovered = set(range(1, m + 1))
    for s in sets:
        uncovered -= s
    
    for element in uncovered:
        random.choice(sets).add(element)
        
    return SCPInstance(m, n, sets)

def generate_adversarial_instance(k: int) -> SCPInstance:
    """
    Generate an adversarial instance for the greedy algorithm.
    This construction forces the greedy algorithm to pick k sets, 
    while the optimal solution uses only 2 sets.
    This is the standard binary construction demonstrating the logarithmic approximation gap.
    """
    if k < 1:
        raise ValueError("k must be at least 1")
        
    # The size of partition P_i is 2^(k - i + 1)
    # Total elements m = 2^(k+1) - 2
    num_elements = 2**(k + 1) - 2
    
    # We will build k greedy sets and 2 optimal sets
    # Total sets n = k + 2
    
    greedy_sets = []
    opt1 = set()
    opt2 = set()
    
    current_element = 1
    for i in range(1, k + 1):
        size = 2**(k - i + 1)
        half_size = size // 2
        
        # Partition elements for this step
        partition_elements = list(range(current_element, current_element + size))
        current_element += size
        
        # Greedy set covers the entire partition
        greedy_sets.append(set(partition_elements))
        
        # Opt sets cover half each
        opt1.update(partition_elements[:half_size])
        opt2.update(partition_elements[half_size:])
        
    # All sets: [opt1, opt2, greedy1, greedy2, ..., greedyk]
    sets = [opt1, opt2] + greedy_sets
    costs = [1.0] * len(sets)
    
    return SCPInstance(num_elements, len(sets), sets, costs)

if __name__ == "__main__":
    inst = generate_uniform_instance(10, 5, 0.3)
    print(f"Uniform: {inst}")
    
    adv = generate_adversarial_instance(4)
    print(f"Adversarial: {adv}")
