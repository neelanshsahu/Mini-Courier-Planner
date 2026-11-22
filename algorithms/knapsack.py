"""
algorithms/knapsack.py
----------------------
0/1 Knapsack solved with Dynamic Programming.

Each parcel has a weight (kg, float) and a value derived from its priority:
    value = priority * 10

Because the standard DP table requires integer weights we scale weights by 10
(i.e. 1 decimal place of precision) and divide the capacity accordingly:
    int_weight = round(weight_kg * 10)
    int_capacity = round(capacity_kg * 10)

Complexity:
    Time:  O(n * W)  where n = number of parcels, W = int_capacity
    Space: O(n * W)  for the full DP table (returned to caller)
"""

import time
from typing import Any, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Core DP solver
# ---------------------------------------------------------------------------

def knapsack_dp(parcels: List[dict], capacity_kg: float) -> Dict[str, Any]:
    """
    Solve the 0/1 Knapsack problem for the given parcels and weight capacity.

    Parameters
    ----------
    parcels      : list of Parcel dicts, each with keys 'weight' and 'priority'
    capacity_kg  : maximum total weight the courier can carry (kilograms, float)

    Returns
    -------
    dict with keys:
        selected     — list of selected Parcel dicts (fit in knapsack)
        rejected     — list of rejected Parcel dicts
        dp_table     — 2D list dp_table[n+1][W+1] showing full DP computation
        total_value  — int, sum of values of selected parcels
        total_weight — float, sum of weights of selected parcels (kg)
        elapsed      — float, wall-clock seconds taken by this function

    Time:  O(n * W)
    Space: O(n * W)
    """
    start = time.perf_counter()

    n = len(parcels)
    # Scale to integers (1 decimal-place precision)
    int_weights = [max(1, round(p["weight"] * 10)) for p in parcels]
    values = [int(p["priority"]) * 10 for p in parcels]
    W = max(1, round(capacity_kg * 10))

    # Build DP table: dp[i][w] = max value using first i items with capacity w
    dp: List[List[int]] = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        iw = int_weights[i - 1]
        iv = values[i - 1]
        for w in range(W + 1):
            # Don't take item i
            dp[i][w] = dp[i - 1][w]
            # Take item i if it fits and improves value
            if iw <= w and dp[i - 1][w - iw] + iv > dp[i][w]:
                dp[i][w] = dp[i - 1][w - iw] + iv

    # Back-track to find which items were selected
    selected_indices = []
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_indices.append(i - 1)   # 0-based index into parcels
            w -= int_weights[i - 1]

    selected_indices_set = set(selected_indices)
    selected = [parcels[i] for i in range(n) if i in selected_indices_set]
    rejected = [parcels[i] for i in range(n) if i not in selected_indices_set]

    total_value = dp[n][W]
    total_weight = round(sum(p["weight"] for p in selected), 4)

    elapsed = time.perf_counter() - start

    return {
        "selected": selected,
        "rejected": rejected,
        "dp_table": dp,
        "total_value": total_value,
        "total_weight": total_weight,
        "elapsed": elapsed,
    }


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

def time_knapsack(parcels: List[dict], capacity: float) -> float:
    """
    Run knapsack_dp and return only the elapsed time in seconds.

    Parameters
    ----------
    parcels  : list of Parcel dicts
    capacity : knapsack capacity in kg

    Returns
    -------
    float — elapsed wall-clock seconds

    Time:  O(n * W)
    Space: O(n * W)
    """
    result = knapsack_dp(parcels, capacity)
    return result["elapsed"]
