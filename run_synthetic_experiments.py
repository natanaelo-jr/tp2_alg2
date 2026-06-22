import os
import time
import csv
import random
import multiprocessing
import numpy as np
import argparse
from typing import Dict, Any, List, Tuple

from scp_types import SCPInstance
from greedy import greedy_scp
from branch_and_bound import BranchAndBoundSolver
from generator import generate_uniform_instance, generate_adversarial_instance

def run_single_task(task_args: Tuple[Dict[str, Any], str, Dict[str, Any], float]) -> Dict[str, Any]:
    """
    Runs a single solver configuration on an instance.
    task_args is a tuple: (instance_info, method, params, timeout)
    """
    inst_info, method, params, timeout = task_args
    
    # Reconstruct/retrieve the instance
    # To avoid passing heavy objects through multiprocessing, we can reconstruct the instance in the worker,
    # or pass it directly. Since our instances are small (m <= 150, n <= 300), passing them directly is fine.
    instance = inst_info["instance"]
    
    start_time = time.time()
    try:
        if method == "greedy":
            sol, cost = greedy_scp(instance)
            nodes = 1
            status = "success"
        elif method == "bb":
            solver = BranchAndBoundSolver(
                instance, 
                strategy=params.get("strategy", "dfs"), 
                lower_bound_type=params.get("lb_type", "sum_degree")
            )
            sol, cost, nodes = solver.solve(timeout=timeout)
            elapsed = time.time() - start_time
            status = "success" if elapsed < timeout else "timeout"
        else:
            raise ValueError(f"Unknown method {method}")
            
        elapsed = time.time() - start_time
        return {
            "instance_type": inst_info["instance_type"],
            "m": inst_info["m"],
            "n": inst_info["n"],
            "p": inst_info.get("p", 0.0),
            "k": inst_info.get("k", 0),
            "instance_id": inst_info["instance_id"],
            "method": method,
            "strategy": params.get("strategy", "N/A"),
            "lb_type": params.get("lb_type", "N/A"),
            "cost": float(cost),
            "time_seconds": elapsed,
            "nodes": nodes,
            "status": status,
            "error": ""
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "instance_type": inst_info["instance_type"],
            "m": inst_info["m"],
            "n": inst_info["n"],
            "p": inst_info.get("p", 0.0),
            "k": inst_info.get("k", 0),
            "instance_id": inst_info["instance_id"],
            "method": method,
            "strategy": params.get("strategy", "N/A"),
            "lb_type": params.get("lb_type", "N/A"),
            "cost": -1.0,
            "time_seconds": elapsed,
            "nodes": 0,
            "status": "error",
            "error": str(e)
        }

def generate_all_tasks(timeout: float, num_uniform: int = 30, num_adv: int = 5) -> List[Tuple[Dict[str, Any], str, Dict[str, Any], float]]:
    tasks = []
    
    # 1. Uniform instances
    # Scales: m = 50, 100, 150 (n = 2m)
    # Densities: p = 0.05, 0.1, 0.2
    # num_uniform instances per configuration
    scales = [50, 100, 150]
    densities = [0.05, 0.1, 0.2]
    
    print("Generating uniform synthetic instances...")
    for m in scales:
        n = 2 * m
        for p in densities:
            # Fix seed for reproducibility but have different seeds
            for inst_id in range(num_uniform):
                # Set seed based on params
                seed = hash((m, n, p, inst_id)) % (2**32)
                random.seed(seed)
                np.random.seed(seed)
                
                instance = generate_uniform_instance(m, n, p)
                
                inst_info = {
                    "instance": instance,
                    "instance_type": "uniform",
                    "m": m,
                    "n": n,
                    "p": p,
                    "k": 0,
                    "instance_id": inst_id
                }
                
                # Add greedy task
                tasks.append((inst_info, "greedy", {}, timeout))
                
                # Add B&B tasks (2 strategies x 3 lower bounds = 6 tasks)
                for strategy in ["dfs", "best_first"]:
                    for lb_type in ["sum_degree", "packing", "both"]:
                        tasks.append((inst_info, "bb", {"strategy": strategy, "lb_type": lb_type}, timeout))
                        
    # 2. Adversarial instances
    # k = 2..10
    # num_adv instances per k (by shuffling element/set indices to test B&B variability)
    print("Generating adversarial synthetic instances...")
    adversarial_ks = list(range(2, 11))
    
    for k in adversarial_ks:
        base_instance = generate_adversarial_instance(k)
        for inst_id in range(num_adv):
            # Shuffle sets and elements of the adversarial instance
            seed = hash((k, inst_id)) % (2**32)
            random.seed(seed)
            
            # Shuffle elements mapping
            m = base_instance.num_elements
            n = base_instance.num_sets
            elem_mapping = list(range(1, m + 1))
            random.shuffle(elem_mapping)
            elem_map_dict = {i + 1: elem_mapping[i] for i in range(m)}
            
            shuffled_sets = []
            for s in base_instance.sets:
                shuffled_s = {elem_map_dict[e] for e in s}
                shuffled_sets.append(shuffled_s)
                
            # Shuffle sets mapping
            sets_order = list(range(n))
            random.shuffle(sets_order)
            
            final_sets = [shuffled_sets[idx] for idx in sets_order]
            final_costs = [base_instance.costs[idx] for idx in sets_order]
            
            instance = SCPInstance(m, n, final_sets, final_costs)
            
            inst_info = {
                "instance": instance,
                "instance_type": "adversarial",
                "m": m,
                "n": n,
                "p": 0.0,
                "k": k,
                "instance_id": inst_id
            }
            
            # Add greedy task
            tasks.append((inst_info, "greedy", {}, timeout))
            
            # Add B&B tasks
            for strategy in ["dfs", "best_first"]:
                for lb_type in ["sum_degree", "packing", "both"]:
                    tasks.append((inst_info, "bb", {"strategy": strategy, "lb_type": lb_type}, timeout))
                    
    print(f"Total tasks generated: {len(tasks)}")
    return tasks

def main():
    parser = argparse.ArgumentParser(description="Run synthetic experiments for SCP solver.")
    parser.add_argument("-o", "--output", type=str, default="results_synthetic.csv",
                        help="Path to output CSV file (default: results_synthetic.csv)")
    parser.add_argument("-t", "--timeout", type=float, default=10800.0,
                        help="Timeout in seconds per solver task (default: 10800.0 (3 hours))")
    parser.add_argument("-u", "--num-uniform", type=int, default=30,
                        help="Number of random uniform instances per configuration (default: 30)")
    parser.add_argument("-a", "--num-adv", type=int, default=5,
                        help="Number of adversarial instances per parameter k (default: 5)")
    parser.add_argument("--quick", action="store_true",
                        help="Run a quick test with 2 uniform and 2 adversarial instances, timeout 10.0s")
    
    args = parser.parse_args()
    
    if args.quick:
        args.timeout = 10.0
        args.num_uniform = 2
        args.num_adv = 2
        
    output_csv = os.path.abspath(args.output)
    timeout = args.timeout
    
    # Generate all tasks
    tasks = generate_all_tasks(timeout, num_uniform=args.num_uniform, num_adv=args.num_adv)
    
    print(f"Starting experiments on {multiprocessing.cpu_count()} cores...")
    start_time = time.time()
    
    results = []
    
    # Initialize the output CSV file and write headers
    fieldnames = [
        "instance_type", "m", "n", "p", "k", "instance_id", 
        "method", "strategy", "lb_type", "cost", "time_seconds", 
        "nodes", "status", "error"
    ]
    try:
        with open(output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    except Exception as e:
        print(f"Error initializing CSV file: {e}")
        return
        
    print(f"Writing results progressively to {output_csv}...")
    
    # Open CSV in append mode to write progressively
    with open(output_csv, 'a', newline='') as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        
        # Process tasks in parallel using multiprocessing Pool
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            # Use imap_unordered for progressive progress reporting
            task_iterator = pool.imap_unordered(run_single_task, tasks, chunksize=1)
            
            total_tasks = len(tasks)
            completed = 0
            
            for result in task_iterator:
                results.append(result)
                
                # Write immediately to CSV
                try:
                    writer.writerow(result)
                    f_csv.flush()
                except Exception as e:
                    print(f"Error writing task result to CSV: {e}")
                    
                completed += 1
                if completed % 100 == 0 or completed == total_tasks:
                    elapsed = time.time() - start_time
                    est_total = (elapsed / completed) * total_tasks if completed > 0 else 0
                    est_remaining = est_total - elapsed
                    print(f"Completed {completed}/{total_tasks} tasks ({completed/total_tasks*100:.1f}%). "
                          f"Elapsed: {elapsed:.1f}s, Est. remaining: {est_remaining:.1f}s")
                          
    total_elapsed = time.time() - start_time
    print(f"Experiments finished successfully in {total_elapsed:.2f} seconds!")

if __name__ == "__main__":
    main()
