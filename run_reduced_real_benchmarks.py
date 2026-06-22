import os
import csv
import time
import multiprocessing
from typing import Dict, Any, List, Tuple

from scp_types import SCPInstance
from benchmark import run_solver

def create_reduced_instance(original_instance: SCPInstance, target_m: int, target_n: int) -> SCPInstance:
    """
    Creates a mathematically valid and feasible sub-instance from the original instance.
    Keeps only elements <= target_m and a subset of sets.
    """
    selected_sets = []
    selected_costs = []
    
    # Select the first target_n sets, filtering elements to only keep those <= target_m
    n_limit = min(target_n, original_instance.num_sets)
    for idx in range(n_limit):
        s = {elem for elem in original_instance.sets[idx] if elem <= target_m}
        selected_sets.append(s)
        selected_costs.append(original_instance.costs[idx])
        
    # Ensure all elements in {1, ..., target_m} are covered
    uncovered = set(range(1, target_m + 1))
    for s in selected_sets:
        uncovered -= s
        
    # For any uncovered elements, pull the first original set that covers them
    if uncovered:
        for elem in list(uncovered):
            # Check if this element is already covered by a set we just added (due to previous elements' search)
            already_covered = False
            for s in selected_sets:
                if elem in s:
                    already_covered = True
                    break
            if already_covered:
                continue
                
            covering_set_idx = -1
            for idx, s in enumerate(original_instance.sets):
                if elem in s:
                    covering_set_idx = idx
                    break
            if covering_set_idx != -1:
                s = {e for e in original_instance.sets[covering_set_idx] if e <= target_m}
                selected_sets.append(s)
                selected_costs.append(original_instance.costs[covering_set_idx])
                
    return SCPInstance(target_m, len(selected_sets), selected_sets, selected_costs)

def benchmark_reduced_instance(original_path: str, output_csv: str, target_m: int, target_n: int, timeout: float):
    # Load original
    orig_instance = SCPInstance.from_or_library(original_path)
    inst_name = os.path.basename(original_path)
    
    # Create reduced
    reduced_instance = create_reduced_instance(orig_instance, target_m, target_n)
    
    # Calculate reduction rates
    m_reduction = (1 - (reduced_instance.num_elements / orig_instance.num_elements)) * 100
    n_reduction = (1 - (reduced_instance.num_sets / orig_instance.num_sets)) * 100
    
    print(f"Reduced {inst_name}:")
    print(f"  Elements: {orig_instance.num_elements} -> {reduced_instance.num_elements} ({m_reduction:.1f}% reduction)")
    print(f"  Sets: {orig_instance.num_sets} -> {reduced_instance.num_sets} ({n_reduction:.1f}% reduction)")
    
    tasks = [
        ("greedy", {}, timeout),
        # DFS with Greedy UB
        ("bb", {"strategy": "dfs", "lb_type": "sum_degree", "initial_ub_type": "greedy"}, timeout),
        ("bb", {"strategy": "dfs", "lb_type": "packing", "initial_ub_type": "greedy"}, timeout),
        ("bb", {"strategy": "dfs", "lb_type": "both", "initial_ub_type": "greedy"}, timeout),
        # DFS with Trivial UB
        ("bb", {"strategy": "dfs", "lb_type": "sum_degree", "initial_ub_type": "trivial"}, timeout),
        ("bb", {"strategy": "dfs", "lb_type": "packing", "initial_ub_type": "trivial"}, timeout),
        ("bb", {"strategy": "dfs", "lb_type": "both", "initial_ub_type": "trivial"}, timeout),
        # Best-First with Greedy UB
        ("bb", {"strategy": "best_first", "lb_type": "sum_degree", "initial_ub_type": "greedy"}, timeout),
        ("bb", {"strategy": "best_first", "lb_type": "packing", "initial_ub_type": "greedy"}, timeout),
        ("bb", {"strategy": "best_first", "lb_type": "both", "initial_ub_type": "greedy"}, timeout),
        # Best-First with Trivial UB
        ("bb", {"strategy": "best_first", "lb_type": "sum_degree", "initial_ub_type": "trivial"}, timeout),
        ("bb", {"strategy": "best_first", "lb_type": "packing", "initial_ub_type": "trivial"}, timeout),
        ("bb", {"strategy": "best_first", "lb_type": "both", "initial_ub_type": "trivial"}, timeout),
    ]
    
    results = []
    # Run in parallel using multiprocessing Pool
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        async_results = [pool.apply_async(run_solver, (reduced_instance, method, params, timeout)) for method, params, _ in tasks]
        for i, res in enumerate(async_results):
            result = res.get()
            result["instance"] = inst_name
            result["orig_m"] = orig_instance.num_elements
            result["orig_n"] = orig_instance.num_sets
            result["red_m"] = reduced_instance.num_elements
            result["red_n"] = reduced_instance.num_sets
            result["m_red_pct"] = m_reduction
            result["n_red_pct"] = n_reduction
            results.append(result)
            
    # Write to CSV
    file_exists = os.path.isfile(output_csv)
    with open(output_csv, 'a', newline='') as f:
        fieldnames = [
            "instance", "orig_m", "orig_n", "red_m", "red_n", 
            "m_red_pct", "n_red_pct", "method", "strategy", "lb_type", "initial_ub_type",
            "cost", "time", "nodes", "status", "error"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for row in results:
            writer.writerow(row)

def main():
    data_dir = "/home/nana/projects/tp2_alg2/data"
    output_csv = "/home/nana/projects/tp2_alg2/results_real_reduced.csv"
    
    # Clear output CSV
    if os.path.exists(output_csv):
        os.remove(output_csv)
        
    all_files = sorted([f for f in os.listdir(data_dir) if f.startswith("scp") and f.endswith(".txt")])
    
    selected_instances = []
    for f in all_files:
        if f.startswith("scp4"):
            selected_instances.append((f, 40, 120))
        elif f.startswith("scp5"):
            selected_instances.append((f, 40, 120))
        elif f.startswith("scp6"):
            selected_instances.append((f, 40, 120))
        elif f.startswith("scpa"):
            selected_instances.append((f, 50, 150))
        elif f.startswith("scpb"):
            selected_instances.append((f, 50, 150))
        elif f.startswith("scpc"):
            selected_instances.append((f, 60, 180))
        elif f.startswith("scpd"):
            selected_instances.append((f, 60, 180))
            
    # 15.0s timeout is more than enough for these small instances and prevents hang
    timeout = 15.0
    
    print(f"Starting reduced real benchmarks for all {len(selected_instances)} instances with timeout={timeout}s...")
    start_time = time.time()
    
    for i, (inst_name, target_m, target_n) in enumerate(selected_instances):
        inst_path = os.path.join(data_dir, inst_name)
        if not os.path.exists(inst_path):
            print(f"Error: {inst_path} does not exist!")
            continue
            
        print(f"\n[{i+1}/{len(selected_instances)}] Benchmarking reduced {inst_name}...")
        try:
            benchmark_reduced_instance(inst_path, output_csv, target_m, target_n, timeout)
        except Exception as e:
            print(f"Error: {e}")
            
    total_elapsed = time.time() - start_time
    print(f"\nAll reduced real benchmarks finished in {total_elapsed:.2f} seconds!")
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    main()
