import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def configure_plt_style():
    """
    Apply a clean, professional, and modern style to Matplotlib.
    """
    plt.rcParams['figure.facecolor'] = '#fdfdfd'
    plt.rcParams['axes.facecolor'] = '#ffffff'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    plt.rcParams['axes.edgecolor'] = '#d3d3d3'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['grid.color'] = '#eaeaea'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['axes.grid'] = True
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 9
    plt.rcParams['legend.frameon'] = True
    plt.rcParams['legend.facecolor'] = '#ffffff'
    plt.rcParams['legend.edgecolor'] = '#e0e0e0'

def label_config(row):
    if row['method'] == 'greedy':
        return 'Guloso'
    
    strat = "DFS" if row['strategy'] == 'dfs' else "Best-First"
    lb = row['lb_type']
    if lb == 'sum_degree':
        lb_label = 'Sum-Degree'
    elif lb == 'packing':
        lb_label = 'Packing'
    elif lb == 'both':
        lb_label = 'Ambos Limitantes'
    else:
        lb_label = lb
        
    return f"B&B {strat} ({lb_label})"

def generate_plots(csv_path: str, output_dir: str):
    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo CSV {csv_path} não encontrado.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    configure_plt_style()
    
    # Load data
    df = pd.read_csv(csv_path)
    if df.empty:
        print("Erro: O arquivo CSV está vazio.")
        return
        
    # Map configuration names for easier plotting
    df['config_label'] = df.apply(label_config, axis=1)
    
    # Separate uniform and adversarial datasets
    df_uni = df[df['instance_type'] == 'uniform'].copy()
    df_adv = df[df['instance_type'] == 'adversarial'].copy()
    
    colors = {
        'Guloso': '#e056fd',
        'B&B DFS (Sum-Degree)': '#ff7675',
        'B&B DFS (Packing)': '#d63031',
        'B&B DFS (Ambos Limitantes)': '#863031',
        'B&B Best-First (Sum-Degree)': '#74b9ff',
        'B&B Best-First (Packing)': '#0984e3',
        'B&B Best-First (Ambos Limitantes)': '#0f3c83',
    }
    
    # --- PLOT 1: Uniform - Time vs. Size m ---
    if not df_uni.empty:
        plt.figure(figsize=(10, 6), dpi=300)
        # Group by configuration and scale m
        grouped_time = df_uni.groupby(['config_label', 'm'])['time_seconds'].mean().reset_index()
        
        for label in colors.keys():
            sub = grouped_time[grouped_time['config_label'] == label]
            if not sub.empty:
                # Sort by m to ensure correct line direction
                sub = sub.sort_values('m')
                plt.plot(sub['m'], sub['time_seconds'], marker='o', linewidth=2, 
                         color=colors[label], label=label)
                         
        plt.title('Tempo de Execução Médio vs. Tamanho da Instância (m)\n(Instâncias Uniformes, n = 2m)')
        plt.xlabel('Tamanho da Instância (m = número de elementos)')
        plt.ylabel('Tempo de Execução Médio (segundos)')
        plt.yscale('log')
        plt.xticks([50, 100, 150])
        plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'uni_time_vs_size.png'), bbox_inches='tight')
        
        # Clean plot for paper
        plt.title('')
        plt.savefig(os.path.join(output_dir, 'uni_time_vs_size_clean.png'), bbox_inches='tight')
        plt.close()
        print("Salvo: uni_time_vs_size.png e uni_time_vs_size_clean.png")
        
        # --- PLOT 2: Uniform - Time vs. Density p ---
        plt.figure(figsize=(10, 6), dpi=300)
        grouped_density = df_uni.groupby(['config_label', 'p'])['time_seconds'].mean().reset_index()
        
        for label in colors.keys():
            sub = grouped_density[grouped_density['config_label'] == label]
            if not sub.empty:
                sub = sub.sort_values('p')
                plt.plot(sub['p'], sub['time_seconds'], marker='s', linewidth=2, 
                         color=colors[label], label=label)
                         
        plt.title('Tempo de Execução Médio vs. Densidade (p)\n(Instâncias Uniformes)')
        plt.xlabel('Densidade (p = probabilidade de elemento pertencer a um conjunto)')
        plt.ylabel('Tempo de Execução Médio (segundos)')
        plt.yscale('log')
        plt.xticks([0.05, 0.1, 0.2])
        plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'uni_time_vs_density.png'), bbox_inches='tight')
        
        # Clean plot for paper
        plt.title('')
        plt.savefig(os.path.join(output_dir, 'uni_time_vs_density_clean.png'), bbox_inches='tight')
        plt.close()
        print("Salvo: uni_time_vs_density.png e uni_time_vs_density_clean.png")

        # --- PLOT 3: Uniform - Nodes Explored vs. Size m ---
        plt.figure(figsize=(10, 6), dpi=300)
        df_bb_uni = df_uni[df_uni['method'] == 'bb']
        if not df_bb_uni.empty:
            grouped_nodes = df_bb_uni.groupby(['config_label', 'm'])['nodes'].mean().reset_index()
            for label in colors.keys():
                if label == 'Guloso':
                    continue
                sub = grouped_nodes[grouped_nodes['config_label'] == label]
                if not sub.empty:
                    sub = sub.sort_values('m')
                    plt.plot(sub['m'], sub['nodes'], marker='^', linewidth=2, 
                             color=colors[label], label=label)
                             
            plt.title('Média de Nós Explorados no B&B vs. Tamanho da Instância (m)\n(Instâncias Uniformes)')
            plt.xlabel('Tamanho da Instância (m)')
            plt.ylabel('Nós Explorados (Escala Logarítmica)')
            plt.yscale('log')
            plt.xticks([50, 100, 150])
            plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'uni_nodes_vs_size.png'), bbox_inches='tight')
            
            # Clean plot for paper
            plt.title('')
            plt.savefig(os.path.join(output_dir, 'uni_nodes_vs_size_clean.png'), bbox_inches='tight')
            plt.close()
            print("Salvo: uni_nodes_vs_size.png e uni_nodes_vs_size_clean.png")

    # --- PLOT 4: Adversarial - Approximation Ratio vs. k ---
    if not df_adv.empty:
        # We need to map optimal costs for each k. 
        # In adversarial instances, OPT cost is always 2.0.
        # Let's verify this and calculate the ratio.
        # Find the optimal cost (which is the min cost found by any bb configuration for that (k, instance_id))
        bb_adv = df_adv[df_adv['method'] == 'bb']
        
        # Calculate optimal cost per (k, instance_id)
        if not bb_adv.empty:
            opt_costs = bb_adv.groupby(['k', 'instance_id'])['cost'].min().reset_index()
            opt_costs.rename(columns={'cost': 'opt_cost'}, inplace=True)
            
            # Merge back to calculate approximation ratio
            df_adv = pd.merge(df_adv, opt_costs, on=['k', 'instance_id'], how='left')
            # Fallback if no B&B solution found: adversarial instance OPT cost is exactly 2.0
            df_adv['opt_cost'] = df_adv['opt_cost'].fillna(2.0)
            df_adv['approx_ratio'] = df_adv['cost'] / df_adv['opt_cost']
            
            # We want to plot the approximation ratio for Greedy vs. k
            greedy_adv = df_adv[df_adv['method'] == 'greedy']
            
            if not greedy_adv.empty:
                plt.figure(figsize=(9, 5), dpi=300)
                
                # Plot individual points with small jitter/alpha to show distribution
                plt.scatter(greedy_adv['k'], greedy_adv['approx_ratio'], alpha=0.3, 
                            color='#e056fd', label='Instâncias individuais')
                
                # Plot mean approximation ratio
                mean_ratio = greedy_adv.groupby('k')['approx_ratio'].mean().reset_index()
                plt.plot(mean_ratio['k'], mean_ratio['approx_ratio'], marker='o', linestyle='-',
                         linewidth=2.5, color='#6c5ce7', label='Razão Média (Empírica)')
                         
                # Plot theoretical worst case: k/2
                k_vals = np.array(sorted(greedy_adv['k'].unique()))
                plt.plot(k_vals, k_vals / 2.0, linestyle='--', color='#d63031', 
                         linewidth=2, label='Pior Caso Teórico ($k/2$)')
                         
                plt.title('Fator de Aproximação do Algoritmo Guloso vs. Parâmetro $k$\n(Instâncias Adversariais)')
                plt.xlabel('Parâmetro k (força o Guloso a escolher k conjuntos)')
                plt.ylabel('Fator de Aproximação ($C_{Guloso} / C_{Otimo}$)')
                plt.xticks(k_vals)
                plt.grid(True, which='both', linestyle='--', alpha=0.5)
                plt.legend(loc='upper left')
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, 'adv_greedy_gap.png'), bbox_inches='tight')
                
                # Clean plot for paper
                plt.title('')
                plt.savefig(os.path.join(output_dir, 'adv_greedy_gap_clean.png'), bbox_inches='tight')
                plt.close()
                print("Salvo: adv_greedy_gap.png e adv_greedy_gap_clean.png")
                
        # --- PLOT 5: Adversarial - Nodes vs. k ---
        plt.figure(figsize=(10, 6), dpi=300)
        df_bb_adv = df_adv[df_adv['method'] == 'bb']
        if not df_bb_adv.empty:
            grouped_adv_nodes = df_bb_adv.groupby(['config_label', 'k'])['nodes'].mean().reset_index()
            
            for label in colors.keys():
                if label == 'Guloso':
                    continue
                sub = grouped_adv_nodes[grouped_adv_nodes['config_label'] == label]
                if not sub.empty:
                    sub = sub.sort_values('k')
                    plt.plot(sub['k'], sub['nodes'], marker='v', linewidth=2, 
                             color=colors[label], label=label)
                             
            plt.title('Média de Nós Explorados no B&B vs. Parâmetro $k$\n(Instâncias Adversariais)')
            plt.xlabel('Parâmetro $k$')
            plt.ylabel('Nós Explorados (Escala Logarítmica)')
            plt.yscale('log')
            plt.xticks(sorted(df_bb_adv['k'].unique()))
            plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'adv_nodes_vs_k.png'), bbox_inches='tight')
            
            # Clean plot for paper
            plt.title('')
            plt.savefig(os.path.join(output_dir, 'adv_nodes_vs_k_clean.png'), bbox_inches='tight')
            plt.close()
            print("Salvo: adv_nodes_vs_k.png e adv_nodes_vs_k_clean.png")
            
    print("Gráficos gerados com sucesso!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera gráficos dos resultados dos experimentos sintéticos.")
    parser.add_argument("-i", "--input", type=str, default="results_synthetic.csv",
                        help="Caminho do arquivo CSV de entrada (padrão: results_synthetic.csv)")
    parser.add_argument("-o", "--output-dir", type=str, default="plots",
                        help="Diretório onde os gráficos serão salvos (padrão: plots)")
    args = parser.parse_args()
    generate_plots(args.input, args.output_dir)
