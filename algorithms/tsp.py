"""
Travelling Salesman Problem (TSP) approximations implemented from scratch.

Algorithms
----------
* Nearest Neighbour heuristic  — O(n²)
* 2-opt local-search improvement — O(n²) per iteration
"""

import math
import time


def _route_distance(route: list[str], distance_matrix: dict) -> float:
    """Return the total distance of a closed route (list includes start == end at tail)."""
    total = 0.0
    for i in range(len(route) - 1):
        frm, to = route[i], route[i + 1]
        total += distance_matrix.get(frm, {}).get(to, math.inf)
    return total


def nearest_neighbor_tsp(
    locations: list[str],
    distance_matrix: dict,
    start: str = "Warehouse",
) -> dict:
    """
    Build a delivery route using the Nearest Neighbour heuristic.

    Starting at `start`, repeatedly visit the closest unvisited location
    until all locations are covered, then return to `start`.

    Parameters
    ----------
    locations : list[str]
        All location names (including `start`).
    distance_matrix : dict[str, dict[str, float]]
        Pairwise shortest distances.
    start : str
        The depot / starting node (default ``"Warehouse"``).

    Returns
    -------
    dict with keys:
        ``route``           — ordered list of node names (start…start)
        ``total_distance``  — float, sum of edge weights
        ``route_segments``  — list of (from, to, distance) tuples

    Time Complexity:  O(n²)
    Space Complexity: O(n)
    """
    if start not in locations:
        raise ValueError(f"Start node '{start}' not in locations list.")

    unvisited = [loc for loc in locations if loc != start]
    route = [start]
    current = start

    while unvisited:
        nearest = None
        nearest_dist = math.inf
        for loc in unvisited:
            d = distance_matrix.get(current, {}).get(loc, math.inf)
            if d < nearest_dist:
                nearest_dist = d
                nearest = loc
        if nearest is None:
            # Graph is disconnected; append remaining in arbitrary order
            route.extend(unvisited)
            break
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    # Return to depot
    route.append(start)

    # Build segments
    segments = []
    for i in range(len(route) - 1):
        frm, to = route[i], route[i + 1]
        d = distance_matrix.get(frm, {}).get(to, math.inf)
        segments.append((frm, to, d))

    total = sum(s[2] for s in segments)

    return {
        "route": route,
        "total_distance": total,
        "route_segments": segments,
    }


def two_opt_improve(route: list[str], distance_matrix: dict) -> dict:
    """
    Apply 2-opt local search to improve a TSP route.

    Iteratively reverses sub-sequences of the route when doing so shortens
    the total distance.  Stops when no improving swap is found.

    Parameters
    ----------
    route : list[str]
        Closed route (first element == last element, e.g. from
        :func:`nearest_neighbor_tsp`).
    distance_matrix : dict[str, dict[str, float]]
        Pairwise shortest distances.

    Returns
    -------
    dict with keys:
        ``route``           — improved (or unchanged) closed route
        ``total_distance``  — float
        ``improvement``     — distance saved vs. the input route (≥ 0)

    Time Complexity:  O(n²) per iteration
    Space Complexity: O(n)
    """
    if len(route) <= 3:
        total = _route_distance(route, distance_matrix)
        return {"route": list(route), "total_distance": total, "improvement": 0.0}

    best_route = list(route)
    best_dist = _route_distance(best_route, distance_matrix)
    original_dist = best_dist
    improved = True

    # The inner nodes are indices 1 … n-2 (index 0 and -1 are both the depot).
    n = len(best_route) - 1  # number of unique nodes visited before returning

    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                # Reverse the segment best_route[i:j+1]
                new_route = (
                    best_route[:i]
                    + best_route[i : j + 1][::-1]
                    + best_route[j + 1 :]
                )
                new_dist = _route_distance(new_route, distance_matrix)
                if new_dist < best_dist - 1e-9:
                    best_route = new_route
                    best_dist = new_dist
                    improved = True

    return {
        "route": best_route,
        "total_distance": best_dist,
        "improvement": original_dist - best_dist,
    }


def time_tsp(locations: list[str], distance_matrix: dict) -> float:
    """
    Measure wall-clock time (seconds) for one run of :func:`nearest_neighbor_tsp`.

    Parameters
    ----------
    locations : list[str]
        Location names.
    distance_matrix : dict[str, dict[str, float]]
        Pairwise distances.

    Returns
    -------
    float
        Elapsed seconds.
    """
    t0 = time.perf_counter()
    nearest_neighbor_tsp(locations, distance_matrix)
    return time.perf_counter() - t0
