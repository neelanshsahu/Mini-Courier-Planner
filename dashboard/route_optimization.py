"""
dashboard/route_optimization.py — Route Optimization page.
"""

import os
import sys
import json

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algorithms.dijkstra import dijkstra, get_shortest_path
from algorithms.tsp import nearest_neighbor_tsp, two_opt_improve
from modules.route_manager import RouteManager

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Fixed x,y positions for the 12 known locations
NODE_POSITIONS = {
    "Warehouse":          (5.0, 5.0),
    "Downtown":           (5.0, 8.0),
    "Airport":            (1.0, 9.0),
    "Mall":               (8.0, 8.0),
    "Hospital":           (3.0, 6.0),
    "University":         (7.0, 3.0),
    "Station":            (5.0, 2.0),
    "Harbor":             (2.0, 2.0),
    "Tech Park":          (9.0, 5.0),
    "Old Town":           (3.0, 9.0),
    "Suburb North":       (6.0, 10.0),
    "Suburb South":       (8.0, 2.0),
}


def _build_graph_fig(graph, highlighted_nodes=None, highlighted_path=None):
    """Build a plotly figure for the graph network."""
    highlighted_nodes = highlighted_nodes or set()
    highlighted_path  = highlighted_path  or []

    # Collect nodes that actually exist in NODE_POSITIONS
    nodes = [n for n in graph if n in NODE_POSITIONS]

    # Edges (draw each undirected edge once)
    seen_edges = set()
    edge_x, edge_y, edge_text = [], [], []
    for u in nodes:
        for v, w in graph[u].items():
            if v not in NODE_POSITIONS:
                continue
            key = tuple(sorted([u, v]))
            if key in seen_edges:
                continue
            seen_edges.add(key)
            x0, y0 = NODE_POSITIONS[u]
            x1, y1 = NODE_POSITIONS[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

    # Highlighted path edges
    path_x, path_y = [], []
    if len(highlighted_path) > 1:
        for i in range(len(highlighted_path) - 1):
            u, v = highlighted_path[i], highlighted_path[i + 1]
            if u in NODE_POSITIONS and v in NODE_POSITIONS:
                x0, y0 = NODE_POSITIONS[u]
                x1, y1 = NODE_POSITIONS[v]
                path_x += [x0, x1, None]
                path_y += [y0, y1, None]

    fig = go.Figure()

    # Base edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(color="rgba(150,150,150,0.5)", width=1.5),
        hoverinfo="none", name="Roads",
    ))

    # Highlighted path
    if path_x:
        fig.add_trace(go.Scatter(
            x=path_x, y=path_y, mode="lines",
            line=dict(color="#e74c3c", width=4),
            hoverinfo="none", name="Selected Route",
        ))

    # Nodes
    node_x = [NODE_POSITIONS[n][0] for n in nodes]
    node_y = [NODE_POSITIONS[n][1] for n in nodes]
    node_colors = []
    for n in nodes:
        if n == "Warehouse":
            node_colors.append("#e74c3c")
        elif n in highlighted_nodes:
            node_colors.append("#f39c12")
        else:
            node_colors.append("#667eea")

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=nodes, textposition="top center",
        marker=dict(size=16, color=node_colors,
                    line=dict(color="white", width=2)),
        hovertemplate="<b>%{text}</b><extra></extra>",
        name="Locations",
    ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=450,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def _load_rm():
    rm = RouteManager()
    loc_path = os.path.join(_BASE, "data", "sample_locations.json")
    if os.path.exists(loc_path):
        rm.load_graph_from_json(loc_path)
    return rm


def show_route_optimization(state):
    st.markdown("<h2 class='section-header'>🗺️ Route Optimization</h2>", unsafe_allow_html=True)

    rm = _load_rm()
    graph = rm.graph

    if not graph:
        st.error("Could not load location graph. Ensure data/sample_locations.json exists.")
        return

    # ── Section 1: Graph View ────────────────────────────────────────────────
    st.markdown("### 1️⃣ Location Network")
    st.markdown(
        "Red = Warehouse hub, Orange = selected destinations, Blue = other locations."
    )
    fig_base = _build_graph_fig(graph)
    st.plotly_chart(fig_base, use_container_width=True)

    st.markdown("---")

    # ── Section 2: Dijkstra ───────────────────────────────────────────────────
    st.markdown("### 2️⃣ Shortest Path (Dijkstra)")
    nodes = list(graph.keys())

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        src = st.selectbox("Source", nodes, index=nodes.index("Warehouse") if "Warehouse" in nodes else 0)
    with d_col2:
        dst_opts = [n for n in nodes if n != src]
        dst = st.selectbox("Destination", dst_opts)

    if st.button("🔍 Find Shortest Path"):
        distances, predecessors = dijkstra(graph, src)
        path = get_shortest_path(predecessors, src, dst)
        dist = distances.get(dst, float("inf"))

        if dist == float("inf"):
            st.error(f"No path found from {src} to {dst}.")
        else:
            st.success(
                f"Shortest path: **{' → '.join(path)}** &nbsp;|&nbsp; "
                f"Distance: **{dist:.2f} km**"
            )
            fig_sp = _build_graph_fig(graph, highlighted_path=path)
            st.plotly_chart(fig_sp, use_container_width=True)

            # Distance table from source
            dist_df = pd.DataFrame([
                {"Destination": n, "Distance (km)": f"{d:.2f}"}
                for n, d in sorted(distances.items(), key=lambda x: x[1])
            ])
            with st.expander("All distances from " + src):
                st.dataframe(dist_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Section 3: TSP Route ─────────────────────────────────────────────────
    st.markdown("### 3️⃣ Delivery Route (TSP — Nearest Neighbor + 2-opt)")

    # Build destination list from knapsack result or let user pick
    knapsack = getattr(state, "knapsack_result", None)
    if knapsack and knapsack.get("selected"):
        kn_dests = list({p["destination"] for p in knapsack["selected"]
                         if p["destination"] in nodes and p["destination"] != "Warehouse"})
    else:
        kn_dests = []

    all_dest_opts = [n for n in nodes if n != "Warehouse"]
    if kn_dests:
        st.info(f"Using {len(kn_dests)} destination(s) from Knapsack result. You can adjust below.")
    
    # Ensure defaults are valid options (filter Warehouse and unknown nodes)
    safe_defaults = [d for d in kn_dests if d in all_dest_opts]
    selected_dests = st.multiselect(
        "Select delivery destinations",
        all_dest_opts,
        default=safe_defaults if safe_defaults else all_dest_opts[:4],
    )

    apply_2opt = st.checkbox("Apply 2-opt improvement", value=True)

    if st.button("🗺️ Run Route Optimization"):
        if not selected_dests:
            st.warning("Select at least one destination.")
        else:
            with st.spinner("Computing delivery route…"):
                result = rm.get_delivery_route(selected_dests, apply_2opt=apply_2opt)
            state.route_result = result

            st.success(
                f"✅ Route computed in **{result['elapsed']*1000:.2f} ms** — "
                f"total distance: **{result['total_distance']:.2f} km**"
            )

    result = getattr(state, "route_result", None)
    if not result:
        st.info("Select destinations and click **Run Route Optimization** to plan the route.")
        return

    route      = result.get("route", [])
    segments   = result.get("segments", [])
    total_dist = result.get("total_distance", 0)
    improvement = result.get("improvement", 0)

    # Route graph highlight
    all_stops  = set(route)
    fig_route  = _build_graph_fig(graph, highlighted_nodes=all_stops, highlighted_path=route)
    st.plotly_chart(fig_route, use_container_width=True)

    # Delivery sequence
    r1, r2, r3 = st.columns(3)
    r1.metric("Total Distance", f"{total_dist:.2f} km")
    r2.metric("Stops",          len(route) - 2)  # exclude start/end Warehouse
    r3.metric("2-opt Improvement", f"{improvement:.2f} km" if improvement else "—")

    st.markdown("**Delivery Sequence:**")
    for i, stop in enumerate(route):
        icon = "🏭" if stop == "Warehouse" else f"📍 Stop {i}"
        st.markdown(f"{i+1}. {icon} **{stop}**")

    # Segment bar chart
    if segments:
        st.markdown("<br>", unsafe_allow_html=True)
        seg_df = pd.DataFrame(segments, columns=["From", "To", "Distance (km)"])
        seg_df["Segment"] = seg_df["From"] + " → " + seg_df["To"]
        fig_seg = px.bar(
            seg_df, x="Segment", y="Distance (km)",
            title="Distance per Route Segment",
            color="Distance (km)",
            color_continuous_scale="Viridis",
        )
        fig_seg.update_layout(
            xaxis_tickangle=-30,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_seg, use_container_width=True)
        st.dataframe(seg_df[["From", "To", "Distance (km)"]], use_container_width=True, hide_index=True)
