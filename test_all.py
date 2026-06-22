from scp_types import SCPInstance
from greedy import greedy_scp
from branch_and_bound import BranchAndBoundSolver
from generator import generate_uniform_instance, generate_adversarial_instance
from utils import get_sum_degree_bound, get_packing_bound

def test_integration():
    print("Testing integration (Uniform)...")
    m, n = 20, 10
    instance = generate_uniform_instance(m, n, 0.2)
    print(f"Generated instance: {instance}")
    
    print("\nRunning Greedy...")
    g_sol, g_cost = greedy_scp(instance)
    print(f"Greedy Cost: {g_cost}")
    
    print("\nRunning B&B (DFS, Both Bounds)...")
    solver_dfs = BranchAndBoundSolver(instance, strategy="dfs", lower_bound_type="both")
    dfs_sol, dfs_cost, dfs_nodes = solver_dfs.solve()
    print(f"DFS B&B Cost: {dfs_cost}, Nodes: {dfs_nodes}")
    
    print("\nRunning B&B (Best-First, Both Bounds)...")
    solver_bf = BranchAndBoundSolver(instance, strategy="best_first", lower_bound_type="both")
    bf_sol, bf_cost, bf_nodes = solver_bf.solve()
    print(f"Best-First B&B Cost: {bf_cost}, Nodes: {bf_nodes}")
    
    assert dfs_cost <= g_cost, "B&B should be at least as good as Greedy"
    assert bf_cost == dfs_cost, "Different B&B strategies should find same optimal cost"
    print("\nIntegration test passed!")

def test_adversarial():
    print("\nTesting Adversarial Instance...")
    k = 4 # Should force greedy to pick 4 sets, while OPT is 2 sets
    instance = generate_adversarial_instance(k)
    print(f"Generated adversarial: {instance} (expect OPT = 2, Greedy = {k})")
    
    g_sol, g_cost = greedy_scp(instance)
    print(f"Greedy sets chosen: {g_sol}, Cost: {g_cost}")
    
    solver = BranchAndBoundSolver(instance, strategy="dfs", lower_bound_type="both")
    opt_sol, opt_cost, nodes = solver.solve()
    print(f"B&B optimal sets chosen: {opt_sol}, Cost: {opt_cost}, Nodes: {nodes}")
    
    assert opt_cost == 2.0, f"Optimal cost should be 2.0, got {opt_cost}"
    assert g_cost == float(k), f"Greedy cost should be {k}, got {g_cost}"
    print("\nAdversarial test passed!")

if __name__ == "__main__":
    test_integration()
    test_adversarial()
