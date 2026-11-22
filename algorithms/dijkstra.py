"""
Dijkstra's shortest path algorithm implemented from scratch using a min-heap priority queue.

Time Complexity:  O((V + E) log V)  where V = nodes, E = edges
Space Complexity: O(V + E)
"""

import heapq
import math
import time


def dijkstra(graph: dict, start: str) -> tuple[dict, dict]:
    """
    Run Dijkstra's algorithm from `start` on `graph`.

    Parameters
    ----------
    graph : dict
        Adjacency representation: {node: {neighbor: weight, ...}, ...}
    start : str
        Source node name.

    Returns
    -------
    distances : dict[str, float]
        Shortest distance from `start` to every reachable node.
        Unreachable nodes map to math.inf.
    predecessors : dict[str, str | None]
        For each node, the node that precedes it on the shortest path from
        `start`.  `start` itself maps to None.

    Time Complexity:  O((V + E) log V)
    Space Complexity: O(V + E)
    """
    distances: dict[str, float] = {node: math.inf for node in graph}
    predecessors: dict[str, str | None] = {node: None for node in graph}

    if start not in distances:
        raise ValueError(f"Start node '{start}' not found in graph.")

    distances[start] = 0.0

    # Min-heap entries: (distance, node)
    heap: list[tuple[float, str]] = [(0.0, start)]

    visited: set[str] = set()

    while heap:
        current_dist, current_node = heapq.heappop(heap)

        if current_node in visited:
            continue
        visited.add(current_node)

        for neighbor, weight in graph.get(current_node, {}).items():
            if neighbor not in distances:
                # Neighbour referenced but not declared as a top-level node
                distances[neighbor] = math.inf
                predecessors[neighbor] = None

            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = current_node
                heapq.heappush(heap, (new_dist, neighbor))

    return distances, predecessors


def get_shortest_path(predecessors: dict, start: str, end: str) -> list[str]:
    """
    Reconstruct the shortest path from `start` to `end` using the
    predecessors dict returned by :func:`dijkstra`.

    Parameters
    ----------
    predecessors : dict[str, str | None]
        Predecessor mapping from :func:`dijkstra`.
    start : str
        Source node.
    end : str
        Destination node.

    Returns
    -------
    list[str]
        Ordered list of node names from `start` to `end`.
        Returns an empty list if no path exists.

    Time Complexity:  O(V)
    Space Complexity: O(V)
    """
    path: list[str] = []
    current: str | None = end

    while current is not None:
        path.append(current)
        if current == start:
            break
        current = predecessors.get(current)
        if current is None and path[-1] != start:
            # No path found
            return []

    path.reverse()
    if not path or path[0] != start:
        return []
    return path


def get_all_pairs_shortest_paths(
    graph: dict, nodes: list[str]
) -> dict[str, dict[str, float]]:
    """
    Compute shortest distances between every pair of nodes in `nodes` by
    running :func:`dijkstra` once from each node.

    Parameters
    ----------
    graph : dict
        Full graph adjacency dict.
    nodes : list[str]
        Subset of node names to include as sources (and sinks).

    Returns
    -------
    dict[str, dict[str, float]]
        all_pairs[src][dst] = shortest distance, or math.inf if unreachable.

    Time Complexity:  O(V * (V + E) log V)  — one Dijkstra per source node
    Space Complexity: O(V²)
    """
    all_pairs: dict[str, dict[str, float]] = {}
    for src in nodes:
        distances, _ = dijkstra(graph, src)
        all_pairs[src] = {dst: distances.get(dst, math.inf) for dst in nodes}
    return all_pairs


def time_dijkstra(graph: dict, start: str) -> float:
    """
    Measure the wall-clock time (in seconds) taken by :func:`dijkstra`.

    Parameters
    ----------
    graph : dict
        Graph adjacency dict.
    start : str
        Source node.

    Returns
    -------
    float
        Elapsed time in seconds.
    """
    t0 = time.perf_counter()
    dijkstra(graph, start)
    return time.perf_counter() - t0
