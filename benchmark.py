import os
import time
import csv
import multiprocessing
import numpy as np
from typing import Dict, Any
from scp_types import SCPInstance
from greedy import greedy_scp
from branch_and_bound import BranchAndBoundSolver

def run_solver(instance: SCPInstance, method: str, params: Dict[str, Any], timeout: float):
    """
    Runner function for a single solver execution.
    """
    start_time = time.time()
    try:
        if method == "greedy":
            sol, cost = greedy_scp(instance)
            nodes = 1
        elif method == "bb":
            solver = BranchAndBoundSolver(
                instance, 
                strategy=params.get("strategy", "dfs"), 
                lower_bound_type=params.get("lb_type", "sum_degree"),
                initial_ub_type=params.get("initial_ub_type", "greedy")
            )
            sol, cost, nodes = solver.solve(timeout=timeout)
        else:
            return None
            
        elapsed = time.time() - start_time
        return {
            "method": method,
            "strategy": params.get("strategy", "N/A"),
            "lb_type": params.get("lb_type", "N/A"),
            "initial_ub_type": params.get("initial_ub_type", "N/A"),
            "cost": cost,
            "time": elapsed,
            "nodes": nodes,
            "status": "success" if elapsed < timeout else "timeout"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def benchmark_instance(instance_path: str, output_csv: str, timeout: float = 10800):
    instance = SCPInstance.from_or_library(instance_path)
    instance_name = os.path.basename(instance_path)
    
    tasks = [
        ("greedy", {}, timeout),
        ("bb", {"strategy": "dfs", "lb_type": "sum_degree"}, timeout),
        ("bb", {"strategy": "best_first", "lb_type": "sum_degree"}, timeout),
        ("bb", {"strategy": "dfs", "lb_type": "packing"}, timeout),
        ("bb", {"strategy": "best_first", "lb_type": "packing"}, timeout),
        ("bb", {"strategy": "dfs", "lb_type": "both"}, timeout),
        ("bb", {"strategy": "best_first", "lb_type": "both"}, timeout),
    ]
    
    results = []
    # Use multiprocessing for different configurations of the same instance
    # Note: For very large instances, we might want to run instances in parallel instead
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        async_results = [pool.apply_async(run_solver, (instance, method, params, t)) for method, params, t in tasks]
        for i, res in enumerate(async_results):
            result = res.get()
            result["instance"] = instance_name
            results.append(result)
            
    # Write to CSV
    file_exists = os.path.isfile(output_csv)
    with open(output_csv, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["instance", "method", "strategy", "lb_type", "cost", "time", "nodes", "status", "error"])
        if not file_exists:
            writer.writeheader()
        for row in results:
            writer.writerow(row)

if __name__ == "__main__":
    # Example usage (commented out as we don't have real instances yet)
    # benchmark_instance("data/scp41.txt", "results.csv")
    print("Benchmarking script ready. Use benchmark_instance() to run tests.")
