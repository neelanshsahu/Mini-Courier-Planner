"""
dashboard/performance_analytics.py — Performance Analytics page.
"""

import os
import sys
import json
import time
import random
import string
from datetime import date, timedelta

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Synthetic data generators (mirror performance_analysis.py) ───────────────

def _generate_parcels(n, seed=42):
    rng = random.Random(seed)
    parcels = []
    base = date(2026, 12, 1)
    for i in range(n):
        priority = rng.randint(1, 5)
        weight   = round(rng.uniform(0.5, 25.0), 2)
        offset   = rng.randint(1, 90)
        deadline = (base + timedelta(days=offset)).strftime("%Y-%m-%d")
        parcels.append({
            "id": f"P{i+1:04d}",
            "name": f"Parcel-{''.join(rng.choices(string.ascii_uppercase, k=4))}",
            "weight": weight, "priority": priority,
            "deadline": deadline, "destination": "Downtown",
            "value": priority * 10,
        })
    return parcels


def _generate_graph(n, seed=42):
    rng = random.Random(seed)
    nodes = [f"N{i}" for i in range(n)]
    graph = {node: {} for node in nodes}
    shuffled = nodes[:]
    rng.shuffle(shuffled)
    connected = [shuffled[0]]
    for node in shuffled[1:]:
        neighbor = rng.choice(connected)
        w = round(rng.uniform(1.0, 50.0), 2)
        graph[node][neighbor] = w
        graph[neighbor][node] = w
        connected.append(node)
    for _ in range(max(1, int(n * 0.3))):
        u, v = rng.choice(nodes), rng.choice(nodes)
        if u != v and v not in graph[u]:
            w = round(rng.uniform(1.0, 50.0), 2)
            graph[u][v] = w
            graph[v][u] = w
    return graph


def _bench(fn, *args, runs=3):
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn(*args)
        times.append(time.perf_counter() - t0)
    return sum(times) / len(times)


def _run_benchmarks():
    from algorithms.sorting import sort_by_combined
    from algorithms.knapsack import knapsack_dp
    from algorithms.dijkstra import dijkstra
    from algorithms.tsp import nearest_neighbor_tsp

    PARCEL_SIZES = [10, 25, 50, 100]
    GRAPH_SIZES  = [5, 8, 12, 16]
    CAPACITY     = 50.0
    RUNS         = 3

    results = {}

    # Sorting
    sorting = {}
    for n in PARCEL_SIZES:
        parcels = _generate_parcels(n)
        sorting[str(n)] = round(_bench(sort_by_combined, parcels, runs=RUNS), 8)
    results["sorting"] = sorting

    # Knapsack
    knapsack = {}
    for n in PARCEL_SIZES:
        parcels = _generate_parcels(n)
        knapsack[str(n)] = round(_bench(knapsack_dp, parcels, CAPACITY, runs=RUNS), 8)
    results["knapsack"] = knapsack

    # Dijkstra
    dijkstra_res = {}
    for n in GRAPH_SIZES:
        graph = _generate_graph(n)
        start = list(graph.keys())[0]
        dijkstra_res[str(n)] = round(_bench(dijkstra, graph, start, runs=RUNS), 8)
    results["dijkstra"] = dijkstra_res

    # TSP
    tsp_res = {}
    for n in GRAPH_SIZES:
        graph = _generate_graph(n)
        nodes = list(graph.keys())
        dist_matrix = {}
        for u in nodes:
            dist_matrix[u] = {}
            for v in nodes:
                if u == v:
                    dist_matrix[u][v] = 0.0
                elif v in graph[u]:
                    dist_matrix[u][v] = graph[u][v]
                else:
                    dist_matrix[u][v] = 9999.0
        start = nodes[0]
        tsp_res[str(n)] = round(_bench(nearest_neighbor_tsp, nodes, dist_matrix, start, runs=RUNS), 8)
    results["tsp"] = tsp_res

    return results


COMPLEXITY_TABLE = [
    {"Algorithm": "Merge Sort",         "Time Complexity": "O(n log n)", "Space Complexity": "O(n)",
     "Best Use Case": "Sorting parcels by priority, deadline, or combined criteria"},
    {"Algorithm": "0/1 Knapsack DP",    "Time Complexity": "O(n × W)",  "Space Complexity": "O(n × W)",
     "Best Use Case": "Selecting optimal parcel set within vehicle weight limit"},
    {"Algorithm": "Dijkstra's SSSP",    "Time Complexity": "O((V+E) log V)", "Space Complexity": "O(V + E)",
     "Best Use Case": "Finding shortest delivery path between two locations"},
    {"Algorithm": "Nearest Neighbor TSP","Time Complexity": "O(n²)",     "Space Complexity": "O(n)",
     "Best Use Case": "Approximate full delivery tour visiting all stops"},
]


def show_performance_analytics(state):
    st.markdown("<h2 class='section-header'>📊 Performance Analytics</h2>", unsafe_allow_html=True)

    # Run benchmarks button
    if st.button("▶️ Run Performance Benchmarks"):
        with st.spinner("Benchmarking all algorithms — this may take a few seconds…"):
            results = _run_benchmarks()
        state.performance_data = results
        # Save to disk
        perf_path = os.path.join(_BASE, "results", "performance_results.json")
        os.makedirs(os.path.dirname(perf_path), exist_ok=True)
        with open(perf_path, "w") as f:
            json.dump(results, f, indent=2)
        st.success("✅ Benchmarks complete. Results saved to results/performance_results.json")

    perf = getattr(state, "performance_data", {})

    if not perf:
        st.info(
            "Click **Run Performance Benchmarks** above to measure execution times.\n\n"
            "Or run `python testing/performance_analysis.py` from the terminal and reload."
        )
        # Try loading from disk
        perf_path = os.path.join(_BASE, "results", "performance_results.json")
        if os.path.exists(perf_path):
            with open(perf_path) as f:
                try:
                    perf = json.load(f)
                    if perf:
                        state.performance_data = perf
                        st.info("Loaded cached results from disk.")
                except Exception:
                    pass
        if not perf:
            return

    st.markdown("---")

    # ── Individual algorithm charts ──────────────────────────────────────────
    st.markdown("### 📈 Execution Time vs Input Size")

    algo_labels = {
        "sorting":  ("Merge Sort",          "Parcels",  "s"),
        "knapsack": ("0/1 Knapsack DP",     "Parcels",  "s"),
        "dijkstra": ("Dijkstra SSSP",       "Nodes",    "s"),
        "tsp":      ("Nearest Neighbor TSP","Nodes",    "s"),
    }

    chart_cols = st.columns(2)
    algo_order = ["sorting", "knapsack", "dijkstra", "tsp"]

    for idx, algo in enumerate(algo_order):
        if algo not in perf:
            continue
        label, x_label, y_unit = algo_labels[algo]
        sizes = list(perf[algo].keys())
        times = list(perf[algo].values())

        fig = px.line(
            x=sizes, y=times,
            markers=True,
            title=label,
            labels={"x": x_label, "y": f"Mean Time ({y_unit})"},
            color_discrete_sequence=["#667eea"],
        )
        fig.update_traces(marker=dict(size=8))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=300,
        )
        with chart_cols[idx % 2]:
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Combined chart ────────────────────────────────────────────────────────
    st.markdown("### 📊 Combined Algorithm Comparison")
    fig_combined = go.Figure()

    colors = ["#667eea", "#764ba2", "#f39c12", "#27ae60"]
    for algo, color in zip(algo_order, colors):
        if algo not in perf:
            continue
        label = algo_labels[algo][0]
        sizes = [str(s) for s in perf[algo].keys()]
        times = list(perf[algo].values())
        fig_combined.add_trace(go.Scatter(
            x=sizes, y=times,
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2),
            marker=dict(size=7),
        ))

    fig_combined.update_layout(
        title="All Algorithms — Size vs Time",
        xaxis_title="Input Size",
        yaxis_title="Mean Time (s)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400,
    )
    st.plotly_chart(fig_combined, use_container_width=True)

    st.markdown("---")

    # ── Complexity table ──────────────────────────────────────────────────────
    st.markdown("### 📋 Complexity Reference")
    df_cplx = pd.DataFrame(COMPLEXITY_TABLE)
    st.dataframe(df_cplx, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Dataset size comparison table ─────────────────────────────────────────
    st.markdown("### 📐 Measured Dataset Sizes")
    rows = []
    for algo in algo_order:
        if algo not in perf:
            continue
        label = algo_labels[algo][0]
        x_label = algo_labels[algo][1]
        for size, t in perf[algo].items():
            rows.append({
                "Algorithm": label,
                f"Input Size ({x_label})": size,
                "Mean Time (s)": f"{t:.8f}",
                "Mean Time (ms)": f"{t*1000:.4f}",
            })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
