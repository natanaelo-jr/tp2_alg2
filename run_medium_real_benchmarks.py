import os
import time
from run_reduced_real_benchmarks import create_reduced_instance, benchmark_reduced_instance

def main():
    data_dir = "/home/nana/projects/tp2_alg2/data"
    output_csv = "/home/nana/projects/tp2_alg2/results_real_medium.csv"
    
    if os.path.exists(output_csv):
        os.remove(output_csv)
        
    selected_instances = [
        # (filename, target_m, target_n)
        # We target m=85, n=425 for scp41.txt (Class SCP4)
        # This is larger than 40 but smaller than 200, representing a medium scale.
        # It is expected to take between 10 minutes and 2 hours for B&B algorithms.
        ("scp41.txt", 85, 425),
        
        # We target m=85, n=850 for scp51.txt (Class SCP5)
        ("scp51.txt", 85, 850),
        
        # For scp61.txt, the density is higher (5%), which makes B&B much more difficult.
        # We target m=70, n=350.
        ("scp61.txt", 70, 350)
    ]
    
    # 3 hours timeout (10800.0 seconds)
    timeout = 10800.0
    
    print(f"Starting medium-sized real benchmarks with timeout={timeout}s...")
    start_time = time.time()
    
    for i, (inst_name, target_m, target_n) in enumerate(selected_instances):
        inst_path = os.path.join(data_dir, inst_name)
        if not os.path.exists(inst_path):
            print(f"Error: {inst_path} does not exist!")
            continue
            
        print(f"\n[{i+1}/{len(selected_instances)}] Benchmarking medium {inst_name} (m={target_m}, n={target_n})...")
        try:
            benchmark_reduced_instance(inst_path, output_csv, target_m, target_n, timeout)
        except Exception as e:
            print(f"Error: {e}")
            
    total_elapsed = time.time() - start_time
    print(f"\nAll medium-sized real benchmarks finished in {total_elapsed:.2f} seconds!")
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    main()
