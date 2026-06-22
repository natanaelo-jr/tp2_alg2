import os
import time
import csv
import glob
from benchmark import benchmark_instance

def main():
    data_dir = "/home/nana/projects/tp2_alg2/data"
    output_csv = "/home/nana/projects/tp2_alg2/results_real.csv"
    
    # Get all scp*.txt files
    instance_files = glob.glob(os.path.join(data_dir, "scp*.txt"))
    # Sort them naturally (e.g. scp41, scp42, scpa1...)
    instance_files.sort(key=lambda x: os.path.basename(x))
    
    print(f"Found {len(instance_files)} real instances in {data_dir}.")
    
    # Initialize/clear the output CSV file
    if os.path.exists(output_csv):
        os.remove(output_csv)
        
    # We will use a timeout of 15.0 seconds per solver run
    # With 7 configurations per instance, and 45 instances:
    # With 15.0s timeout and 8 CPU cores, worst-case time is ~11 minutes.
    timeout = 15.0
    
    print(f"Starting benchmarks on {len(instance_files)} instances with timeout={timeout}s per configuration...")
    start_time = time.time()
    
    for i, inst_path in enumerate(instance_files):
        inst_name = os.path.basename(inst_path)
        print(f"[{i+1}/{len(instance_files)}] Benchmarking {inst_name}...")
        try:
            benchmark_instance(inst_path, output_csv, timeout=timeout)
        except Exception as e:
            print(f"Error benching {inst_name}: {e}")
            
    total_elapsed = time.time() - start_time
    print(f"\nAll real instances benchmarks finished in {total_elapsed:.2f} seconds!")
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    main()
