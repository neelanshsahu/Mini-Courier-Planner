"""
algorithms/sorting.py
---------------------
Merge Sort implementation for sorting Parcel dicts.

All public functions operate on lists of Parcel dicts.

Complexity (merge_sort):
    Time:  O(n log n) — divides the array in halves each recursion level
    Space: O(n)       — auxiliary arrays created during the merge step
"""

import time
from typing import Any, Callable, List, Tuple


# ---------------------------------------------------------------------------
# Core merge sort
# ---------------------------------------------------------------------------

def merge_sort(arr: List[Any], key_fn: Callable[[Any], Any]) -> List[Any]:
    """
    Recursively sort *arr* by the value returned by *key_fn*.

    Parameters
    ----------
    arr     : list of items to sort (not mutated; a new list is returned)
    key_fn  : callable that accepts one element and returns a comparable key

    Returns
    -------
    A new list sorted in ascending order of key_fn(element).

    Time:  O(n log n)
    Space: O(n)
    """
    if len(arr) <= 1:
        return list(arr)

    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key_fn)
    right = merge_sort(arr[mid:], key_fn)
    return _merge(left, right, key_fn)


def _merge(left: List[Any], right: List[Any], key_fn: Callable[[Any], Any]) -> List[Any]:
    """Merge two sorted lists into one sorted list."""
    result: List[Any] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key_fn(left[i]) <= key_fn(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ---------------------------------------------------------------------------
# Convenience sorting functions
# ---------------------------------------------------------------------------

def sort_by_priority(parcels: List[dict]) -> List[dict]:
    """
    Sort parcels by priority in *descending* order (highest priority first).

    Time:  O(n log n)
    Space: O(n)
    """
    # Negate priority so merge_sort (ascending) gives descending result
    return merge_sort(parcels, key_fn=lambda p: -p["priority"])


def sort_by_deadline(parcels: List[dict]) -> List[dict]:
    """
    Sort parcels by deadline in *ascending* order (earliest deadline first).

    Deadlines are stored as 'YYYY-MM-DD' strings, so lexicographic order
    equals chronological order.

    Time:  O(n log n)
    Space: O(n)
    """
    return merge_sort(parcels, key_fn=lambda p: p["deadline"])


def sort_by_combined(parcels: List[dict]) -> List[dict]:
    """
    Sort parcels by a combined key:
        primary   — priority *descending* (higher number = more urgent)
        secondary — deadline *ascending*  (earlier date = more urgent)

    Returns a stable sort: parcels with the same priority are ordered
    by deadline; parcels with the same priority and deadline keep their
    relative original order.

    Time:  O(n log n)
    Space: O(n)
    """
    return merge_sort(parcels, key_fn=lambda p: (-p["priority"], p["deadline"]))


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

def time_sort(parcels: List[dict], sort_fn: Callable[[List[dict]], List[dict]]) -> Tuple[List[dict], float]:
    """
    Run *sort_fn* on *parcels* and measure wall-clock elapsed time.

    Parameters
    ----------
    parcels : list of Parcel dicts
    sort_fn : one of sort_by_priority, sort_by_deadline, sort_by_combined
              (or any callable that accepts a list and returns a sorted list)

    Returns
    -------
    (sorted_list, elapsed_seconds)
        sorted_list     — the result returned by sort_fn
        elapsed_seconds — float, wall-clock seconds taken by sort_fn

    Time:  O(n log n) — dominated by sort_fn
    Space: O(n)
    """
    start = time.perf_counter()
    result = sort_fn(parcels)
    elapsed = time.perf_counter() - start
    return result, elapsed
