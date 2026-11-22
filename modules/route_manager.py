"""
RouteManager — high-level façade for graph loading, shortest-path computation,
and delivery route optimisation.

Depends on:
    algorithms.dijkstra  (Dijkstra's shortest-path)
    algorithms.tsp       (Nearest-Neighbour TSP + 2-opt)
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

from algorithms.dijkstra import dijkstra, get_all_pairs_shortest_paths
from algorithms.tsp import nearest_neighbor_tsp, two_opt_improve


class RouteManager:
    """
    Manages a road-network graph and computes optimal delivery routes.

    Attributes
    ----------
    graph : dict[str, dict[str, float]]
        Undirected adjacency representation loaded from JSON.
    locations : list[str]
        All node names currently in the graph.
    distance_matrix : dict[str, dict[str, float]]
        All-pairs shortest-path distances (populated by
        :meth:`compute_distance_matrix`).
    """

    def __init__(self) -> None:
        self.graph: dict[str, dict[str, float]] = {}
        self.locations: list[str] = []
        self.distance_matrix: dict[str, dict[str, float]] = {}

    # ------------------------------------------------------------------
    # Graph loading / building
    # ------------------------------------------------------------------

    def load_graph_from_json(self, filepath: str) -> None:
        """
        Load the road-network graph from a JSON file.

        Expected format::

            {
              "nodes": ["Warehouse", "Downtown", ...],
              "edges": [["Warehouse", "Downtown", 3.5], ...]
            }

        The graph is stored as an undirected adjacency dict.

        Parameters
        ----------
        filepath : str
            Path to the JSON file (e.g. ``data/sample_locations.json``).
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Graph JSON not found: {filepath}")

        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

        nodes: list[str] = data.get("nodes", [])
        edges: list[list] = data.get("edges", [])

        # Initialise adjacency dict
        graph: dict[str, dict[str, float]] = {n: {} for n in nodes}

        for edge in edges:
            frm, to, weight = edge[0], edge[1], float(edge[2])
            graph.setdefault(frm, {})[to] = weight
            graph.setdefault(to, {})[frm] = weight  # undirected

        self.graph = graph
        self.locations = list(graph.keys())

    def build_graph_from_locations(self, location_list: list[str]) -> dict:
        """
        Return a subgraph (or fallback grid graph) for the given locations.

        If ``self.graph`` has already been loaded (via
        :meth:`load_graph_from_json`), this method returns the loaded graph
        filtered to only include edges where *both* endpoints are in
        ``location_list``.

        If the graph is empty, a simple fully-connected grid graph is
        constructed using ascending integer distances so that every location
        is reachable.

        Parameters
        ----------
        location_list : list[str]
            Names of locations to include.

        Returns
        -------
        dict
            Filtered / constructed adjacency graph.
        """
        location_set = set(location_list)

        if self.graph:
            # Filter existing graph to the requested subset
            sub: dict[str, dict[str, float]] = {}
            for node in location_list:
                sub[node] = {
                    nb: w
                    for nb, w in self.graph.get(node, {}).items()
                    if nb in location_set
                }
            # Update internal state
            self.graph = sub
            self.locations = list(sub.keys())
            return sub

        # Fallback: build a simple chain-plus-cross-links grid so the graph
        # is always connected.
        fallback: dict[str, dict[str, float]] = {loc: {} for loc in location_list}
        n = len(location_list)
        base_dist = 5.0
        for i in range(n):
            for j in range(i + 1, n):
                dist = base_dist * (j - i)
                fallback[location_list[i]][location_list[j]] = dist
                fallback[location_list[j]][location_list[i]] = dist

        self.graph = fallback
        self.locations = list(fallback.keys())
        return fallback

    # ------------------------------------------------------------------
    # Distance matrix
    # ------------------------------------------------------------------

    def compute_distance_matrix(self, locations: list[str]) -> dict:
        """
        Compute all-pairs shortest-path distances for the given locations
        using Dijkstra's algorithm and cache the result.

        Parameters
        ----------
        locations : list[str]
            Location names to include.

        Returns
        -------
        dict[str, dict[str, float]]
            ``matrix[src][dst]`` = shortest distance in km (or ``math.inf``
            if unreachable).
        """
        if not self.graph:
            raise RuntimeError(
                "Graph is empty. Call load_graph_from_json() or "
                "build_graph_from_locations() first."
            )
        matrix = get_all_pairs_shortest_paths(self.graph, locations)
        self.distance_matrix = matrix
        return matrix

    # ------------------------------------------------------------------
    # Delivery route
    # ------------------------------------------------------------------

    def get_delivery_route(
        self,
        selected_destinations: list[str],
        apply_2opt: bool = True,
    ) -> dict:
        """
        Plan an optimised delivery route that starts and ends at ``"Warehouse"``.

        Steps
        -----
        1. Ensure ``"Warehouse"`` is in the destination list.
        2. Compute (or reuse) the distance matrix.
        3. Run Nearest-Neighbour TSP.
        4. Optionally apply 2-opt improvement.

        Parameters
        ----------
        selected_destinations : list[str]
            Delivery stop names (do *not* need to include ``"Warehouse"``).
        apply_2opt : bool
            Whether to apply the 2-opt local-search pass (default: ``True``).

        Returns
        -------
        dict with keys:
            ``route``          — ordered list of node names (depot … depot)
            ``total_distance`` — float, total km
            ``segments``       — list of (from, to, distance) tuples
            ``improvement``    — km saved by 2-opt (0.0 if not applied)
            ``elapsed``        — wall-clock seconds for the whole call
        """
        t0 = time.perf_counter()

        # Filter out destinations that are not known graph nodes
        known_nodes = set(self.graph.keys())
        all_stops = [d for d in selected_destinations if d in known_nodes]
        if "Warehouse" not in all_stops:
            all_stops = ["Warehouse"] + all_stops

        # Recompute distance matrix if the stop set changed
        needed = set(all_stops)
        cached = set(self.distance_matrix.keys())
        if not needed.issubset(cached):
            self.compute_distance_matrix(all_stops)

        # Narrow down the cached matrix to the requested stops
        dm = {
            src: {dst: self.distance_matrix[src][dst] for dst in all_stops}
            for src in all_stops
        }

        nn_result = nearest_neighbor_tsp(all_stops, dm, start="Warehouse")

        improvement = 0.0
        route = nn_result["route"]
        total_distance = nn_result["total_distance"]
        segments = nn_result["route_segments"]

        if apply_2opt:
            opt_result = two_opt_improve(route, dm)
            route = opt_result["route"]
            total_distance = opt_result["total_distance"]
            improvement = opt_result["improvement"]

            # Rebuild segments for the optimised route
            segments = []
            for i in range(len(route) - 1):
                frm, to = route[i], route[i + 1]
                d = dm.get(frm, {}).get(to, math.inf)
                segments.append((frm, to, d))

        elapsed = time.perf_counter() - t0

        return {
            "route": route,
            "total_distance": total_distance,
            "segments": segments,
            "improvement": improvement,
            "elapsed": elapsed,
        }

    # ------------------------------------------------------------------
    # Graph inspection
    # ------------------------------------------------------------------

    def get_graph_edges(self) -> list[tuple[str, str, float]]:
        """
        Return every edge in the graph as a flat list.

        Each edge is represented once in each direction (since the graph is
        undirected); if you want unique edges, deduplicate by sorted pair.

        Returns
        -------
        list[tuple[str, str, float]]
            List of ``(from_node, to_node, weight)`` tuples.
        """
        edges: list[tuple[str, str, float]] = []
        for frm, neighbours in self.graph.items():
            for to, weight in neighbours.items():
                edges.append((frm, to, weight))
        return edges
