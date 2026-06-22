import os
import random
import numpy as np
from generator import generate_uniform_instance, generate_adversarial_instance

def main():
    output_dir = "/home/nana/projects/tp2_alg2/data/synthetic"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating and saving synthetic instances to data/synthetic/...")
    
    # 1. Generate Uniform Instances
    # Scales: m = 50, 100, 150 (n = 2m)
    # Densities: p = 0.05, 0.1, 0.2
    # 30 instances per config
    scales = [50, 100, 150]
    densities = [0.05, 0.1, 0.2]
    num_uniform = 30
    
    uniform_count = 0
    for m in scales:
        n = 2 * m
        for p in densities:
            for inst_id in range(num_uniform):
                # Unique seed for reproducibility
                seed = hash((m, n, p, inst_id)) % (2**32)
                random.seed(seed)
                np.random.seed(seed)
                
                instance = generate_uniform_instance(m, n, p)
                
                # Format density string without dots for filenames (e.g., 0.05 -> 005)
                p_str = str(p).replace('.', '')
                filename = f"uniform_m{m}_n{n}_p{p_str}_id{inst_id}.txt"
                filepath = os.path.join(output_dir, filename)
                
                instance.to_or_library(filepath)
                uniform_count += 1
                
    print(f"Generated {uniform_count} uniform instances.")
    
    # 2. Generate Adversarial Instances
    # k from 2 to 10
    # 5 instances per k
    num_adv = 5
    adv_count = 0
    for k in range(2, 11):
        for inst_id in range(num_adv):
            # Unique seed
            seed = hash((k, inst_id)) % (2**32)
            random.seed(seed)
            np.random.seed(seed)
            
            instance = generate_adversarial_instance(k)
            
            filename = f"adversarial_k{k}_id{inst_id}.txt"
            filepath = os.path.join(output_dir, filename)
            
            instance.to_or_library(filepath)
            adv_count += 1
            
    print(f"Generated {adv_count} adversarial instances.")
    print("All synthetic instances saved successfully in data/synthetic/!")

if __name__ == "__main__":
    main()
