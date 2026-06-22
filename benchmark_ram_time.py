import os
import time
import csv
import multiprocessing
import tracemalloc
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Tuple

from scp_types import SCPInstance
from greedy import greedy_scp
from branch_and_bound import BranchAndBoundSolver
from run_reduced_real_benchmarks import create_reduced_instance

def run_solver_with_mem(instance: SCPInstance, method: str, params: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    """
    Runs a solver configuration and measures both execution time and peak memory (RAM).
    """
    tracemalloc.start()
    start_time = time.time()
    try:
        if method == "greedy":
            sol, cost = greedy_scp(instance)
            nodes = 1
        elif method == "bb":
            solver = BranchAndBoundSolver(
                instance, 
                strategy=params.get("strategy", "dfs"), 
                lower_bound_type=params.get("lb_type", "sum_degree")
            )
            sol, cost, nodes = solver.solve(timeout=timeout)
        else:
            return {"status": "error", "error": "Unknown method"}
            
        elapsed = time.time() - start_time
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "method": method,
            "strategy": params.get("strategy", "N/A"),
            "lb_type": params.get("lb_type", "N/A"),
            "cost": cost,
            "time": elapsed,
            "memory_mb": peak / (1024.0 * 1024.0),
            "nodes": nodes,
            "status": "success" if elapsed < timeout else "timeout"
        }
    except Exception as e:
        tracemalloc.stop()
        return {
            "status": "error", 
            "error": str(e), 
            "time": 0.0, 
            "memory_mb": 0.0, 
            "nodes": 0, 
            "cost": -1.0
        }

def run_task_wrapper(args):
    # Unpack args and run
    instance, method, params, timeout, inst_name, m, n = args
    res = run_solver_with_mem(instance, method, params, timeout)
    res["instance"] = inst_name
    res["m"] = m
    res["n"] = n
    return res

def main():
    data_dir = "/home/nana/projects/tp2_alg2/data"
    output_csv = "/home/nana/projects/tp2_alg2/results_ram_time.csv"
    
    # We will test scp41.txt at different scales to see curves of Time and RAM vs Size!
    # Sizes:
    # 1. Reduced: 40 x 121
    # 2. Small-Medium: 60 x 300
    # 3. Medium: 80 x 400
    # 4. Large-Medium: 100 x 500
    scales = [
        ("scp41_40", 40, 121),
        ("scp41_60", 60, 300),
        ("scp41_80", 80, 400),
        ("scp41_100", 100, 500)
    ]
    
    # Timeout of 60.0s is more than enough to capture exponential growth and RAM usage trends
    timeout = 60.0
    
    orig_instance = SCPInstance.from_or_library(os.path.join(data_dir, "scp41.txt"))
    
    tasks = []
    for name, m, n in scales:
        reduced_inst = create_reduced_instance(orig_instance, m, n)
        
        # Configurations
        configs = [
            ("greedy", {}),
            ("bb", {"strategy": "dfs", "lb_type": "sum_degree"}),
            ("bb", {"strategy": "best_first", "lb_type": "sum_degree"}),
            ("bb", {"strategy": "dfs", "lb_type": "packing"}),
            ("bb", {"strategy": "best_first", "lb_type": "packing"}),
            ("bb", {"strategy": "dfs", "lb_type": "both"}),
            ("bb", {"strategy": "best_first", "lb_type": "both"}),
        ]
        
        for method, params in configs:
            tasks.append((reduced_inst, method, params, timeout, name, m, n))
            
    print(f"Starting memory and time benchmarks (Total tasks: {len(tasks)})...")
    start_time = time.time()
    
    # Run in parallel
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(run_task_wrapper, tasks)
        
    # Write to CSV
    fieldnames = ["instance", "m", "n", "method", "strategy", "lb_type", "cost", "time", "memory_mb", "nodes", "status", "error"]
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
            
    print(f"Results saved to {output_csv} in {time.time() - start_time:.2f} seconds!")
    
    # Generate the Memory and Time plots
    df = pd.read_csv(output_csv)
    
    # Label mapping for clean plotting
    def get_label(row):
        if row['method'] == 'greedy':
            return 'Guloso'
        strat = 'DFS' if row['strategy'] == 'dfs' else 'Best-First'
        lb = row['lb_type']
        if lb == 'sum_degree':
            lb_lbl = 'Sum-Degree'
        elif lb == 'packing':
            lb_lbl = 'Packing'
        else:
            lb_lbl = 'Ambos'
        return f"B&B {strat} ({lb_lbl})"
        
    df['label'] = df.apply(get_label, axis=1)
    
    # Colors matching the previous plots
    colors = {
        'Guloso': '#e056fd',
        'B&B DFS (Sum-Degree)': '#ff7675',
        'B&B DFS (Packing)': '#d63031',
        'B&B DFS (Ambos)': '#863031',
        'B&B Best-First (Sum-Degree)': '#74b9ff',
        'B&B Best-First (Packing)': '#0984e3',
        'B&B Best-First (Ambos)': '#0f3c83',
    }
    
    # Plot 1: Time vs. Size m
    plt.figure(figsize=(10, 6), dpi=300)
    for label, color in colors.items():
        sub = df[df['label'] == label].sort_values('m')
        if not sub.empty:
            plt.plot(sub['m'], sub['time'], marker='o', linewidth=2, color=color, label=label)
    plt.title('Tempo de Execução vs. Tamanho do Universo (m)\n(Sub-instâncias do scp41.txt)')
    plt.xlabel('Tamanho da Instância (m)')
    plt.ylabel('Tempo de Execução (segundos) - Escala Logarítmica')
    plt.yscale('log')
    plt.xticks([40, 60, 80, 100])
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.tight_layout()
    plots_dir = "/home/nana/projects/tp2_alg2/plots"
    os.makedirs(plots_dir, exist_ok=True)
    plt.savefig(os.path.join(plots_dir, 'time_vs_size_ram_time.png'), bbox_inches='tight')
    
    # Clean version (no title)
    plt.title('')
    plt.savefig(os.path.join(plots_dir, 'time_vs_size_ram_time_clean.png'), bbox_inches='tight')
    plt.close()
    
    # Plot 2: Peak Memory (RAM) vs. Size m
    plt.figure(figsize=(10, 6), dpi=300)
    for label, color in colors.items():
        sub = df[df['label'] == label].sort_values('m')
        if not sub.empty:
            plt.plot(sub['m'], sub['memory_mb'], marker='s', linewidth=2, color=color, label=label)
    plt.title('Consumo de Memória RAM Pico vs. Tamanho do Universo (m)\n(Sub-instâncias do scp41.txt)')
    plt.xlabel('Tamanho da Instância (m)')
    plt.ylabel('Memória RAM Pico (Megabytes)')
    plt.xticks([40, 60, 80, 100])
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'ram_vs_size_ram_time.png'), bbox_inches='tight')
    
    # Clean version (no title)
    plt.title('')
    plt.savefig(os.path.join(plots_dir, 'ram_vs_size_ram_time_clean.png'), bbox_inches='tight')
    plt.close()
    
    print("RAM and Time plots generated successfully in plots/!")

if __name__ == "__main__":
    main()
