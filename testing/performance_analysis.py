"""
Performance Analysis — Mini-Courier Planner
============================================
Benchmarks all four algorithm families across a range of input sizes.
Generates synthetic data entirely in-memory (no CSV dependency).

Usage:
    cd "/Users/neelanshsahu/Mini-Courier Planner"
    python testing/performance_analysis.py

Output:
    Prints a formatted summary table to stdout and writes
    results/performance_results.json with the recorded timings.
"""

import sys
import os
import json
import time
import random
import string
from datetime import date, timedelta

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.sorting import sort_by_priority, sort_by_deadline, sort_by_combined
from algorithms.knapsack import knapsack_dp
from algorithms.dijkstra import dijkstra
from algorithms.tsp import nearest_neighbor_tsp


# ---------------------------------------------------------------------------
# Data generators
# ---------------------------------------------------------------------------

DESTINATIONS = [
    "Warehouse", "Downtown", "Airport", "Mall", "Hospital",
    "University", "Station", "Harbor", "Tech Park", "Old Town",
    "Suburb North", "Suburb South", "Industrial Zone",
    "Residential East", "Commercial District",
]


def _random_date(start_days: int = 1, end_days: int = 90) -> str:
    base = date(2026, 12, 1)
    offset = random.randint(start_days, end_days)
    return (base + timedelta(days=offset)).strftime("%Y-%m-%d")


def generate_parcels(n: int, seed: int = 42) -> list:
    """Return n random parcel dicts with no external file dependency."""
    rng = random.Random(seed)
    parcels = []
    for i in range(n):
        priority = rng.randint(1, 5)
        weight = round(rng.uniform(0.5, 25.0), 2)
        parcel = {
            "id": f"P{i+1:04d}",
            "name": f"Parcel-{''.join(rng.choices(string.ascii_uppercase, k=4))}",
            "weight": weight,
            "priority": priority,
            "deadline": _random_date(rng.randint(1, 30), rng.randint(31, 90)),
            "destination": rng.choice(DESTINATIONS),
            "value": priority * 10,
        }
        parcels.append(parcel)
    return parcels


def generate_connected_graph(n: int, seed: int = 42) -> dict:
    """
    Return a random connected undirected graph (as adjacency dict) with n nodes.
    Node names: 'N0', 'N1', ..., 'N{n-1}'.
    Edges have weights 1.0–50.0 km.
    Strategy: build a random spanning tree first (guarantees connectivity),
    then add ~30% extra random edges.
    """
    rng = random.Random(seed)
    nodes = [f"N{i}" for i in range(n)]

    graph = {node: {} for node in nodes}

    # Spanning tree via random insertion order
    shuffled = nodes[:]
    rng.shuffle(shuffled)
    connected = [shuffled[0]]
    for node in shuffled[1:]:
        neighbor = rng.choice(connected)
        w = round(rng.uniform(1.0, 50.0), 2)
        graph[node][neighbor] = w
        graph[neighbor][node] = w
        connected.append(node)

    # Extra random edges
    extra = max(1, int(n * 0.3))
    for _ in range(extra):
        u = rng.choice(nodes)
        v = rng.choice(nodes)
        if u != v and v not in graph[u]:
            w = round(rng.uniform(1.0, 50.0), 2)
            graph[u][v] = w
            graph[v][u] = w

    return graph


# ---------------------------------------------------------------------------
# Benchmark helpers
# ---------------------------------------------------------------------------

def bench(fn, *args, runs: int = 3) -> float:
    """Run fn(*args) `runs` times and return mean elapsed seconds."""
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn(*args)
        times.append(time.perf_counter() - t0)
    return sum(times) / len(times)


# ---------------------------------------------------------------------------
# Algorithm benchmarks
# ---------------------------------------------------------------------------

PARCEL_SIZES = [10, 25, 50, 100]
GRAPH_SIZES  = [5, 8, 12, 16]
RUNS = 3
KNAPSACK_CAPACITY = 50.0  # kg


def benchmark_sorting(parcel_sizes: list, runs: int) -> dict:
    results = {}
    for n in parcel_sizes:
        parcels = generate_parcels(n)
        # Benchmark the most representative combined sort
        elapsed = bench(sort_by_combined, parcels, runs=runs)
        results[str(n)] = round(elapsed, 8)
    return results


def benchmark_knapsack(parcel_sizes: list, runs: int) -> dict:
    results = {}
    for n in parcel_sizes:
        parcels = generate_parcels(n)
        elapsed = bench(knapsack_dp, parcels, KNAPSACK_CAPACITY, runs=runs)
        results[str(n)] = round(elapsed, 8)
    return results


def benchmark_dijkstra(graph_sizes: list, runs: int) -> dict:
    results = {}
    for n in graph_sizes:
        graph = generate_connected_graph(n)
        start_node = list(graph.keys())[0]
        elapsed = bench(dijkstra, graph, start_node, runs=runs)
        results[str(n)] = round(elapsed, 8)
    return results


def benchmark_tsp(graph_sizes: list, runs: int) -> dict:
    results = {}
    for n in graph_sizes:
        graph = generate_connected_graph(n)
        nodes = list(graph.keys())

        # Build a full distance matrix using Dijkstra all-pairs
        # (keep it simple: use raw edge weights as direct distances for TSP bench)
        # For TSP we need a complete distance matrix; use direct edges + inf for missing
        dist_matrix = {}
        for u in nodes:
            dist_matrix[u] = {}
            for v in nodes:
                if u == v:
                    dist_matrix[u][v] = 0.0
                elif v in graph[u]:
                    dist_matrix[u][v] = graph[u][v]
                else:
                    # Use large number to simulate missing (TSP still works)
                    dist_matrix[u][v] = 9999.0

        start = nodes[0]
        elapsed = bench(nearest_neighbor_tsp, nodes, dist_matrix, start, runs=runs)
        results[str(n)] = round(elapsed, 8)
    return results


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------

def print_summary(all_results: dict):
    print()
    print("=" * 70)
    print("  MINI-COURIER PLANNER — ALGORITHM PERFORMANCE BENCHMARK")
    print("=" * 70)

    for algo, timings in all_results.items():
        print(f"\n  {algo.upper()}")
        print(f"  {'Input Size':>12}  {'Mean Time (s)':>16}  {'Relative':>10}")
        print(f"  {'-'*12}  {'-'*16}  {'-'*10}")
        min_t = min(timings.values()) or 1e-12
        for size, t in timings.items():
            rel = f"{t / min_t:.2f}x"
            print(f"  {size:>12}  {t:>16.8f}  {rel:>10}")

    print()
    print("=" * 70)
    print("  Runs per measurement:", RUNS)
    print("  Parcel sizes:", PARCEL_SIZES, "(sorting & knapsack)")
    print("  Graph sizes :", GRAPH_SIZES, "(dijkstra & tsp)")
    print("=" * 70)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Running benchmarks…")

    all_results = {}

    print("  [1/4] Sorting…", end=" ", flush=True)
    all_results["sorting"] = benchmark_sorting(PARCEL_SIZES, RUNS)
    print("done")

    print("  [2/4] Knapsack…", end=" ", flush=True)
    all_results["knapsack"] = benchmark_knapsack(PARCEL_SIZES, RUNS)
    print("done")

    print("  [3/4] Dijkstra…", end=" ", flush=True)
    all_results["dijkstra"] = benchmark_dijkstra(GRAPH_SIZES, RUNS)
    print("done")

    print("  [4/4] TSP…", end=" ", flush=True)
    all_results["tsp"] = benchmark_tsp(GRAPH_SIZES, RUNS)
    print("done")

    # Save results
    results_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "results", "performance_results.json"
    )
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    print_summary(all_results)


if __name__ == "__main__":
    main()
