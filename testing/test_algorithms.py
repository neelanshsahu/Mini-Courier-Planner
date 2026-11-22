"""
Unit tests for Mini-Courier Planner algorithms.

Run with:
    cd "/Users/neelanshsahu/Mini-Courier Planner"
    python -m pytest testing/test_algorithms.py -v
"""

import unittest
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.sorting import sort_by_priority, sort_by_deadline, sort_by_combined
from algorithms.knapsack import knapsack_dp
from algorithms.dijkstra import dijkstra, get_shortest_path
from algorithms.tsp import nearest_neighbor_tsp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_parcel(pid, name, weight, priority, deadline, destination):
    return {
        "id": pid,
        "name": name,
        "weight": weight,
        "priority": priority,
        "deadline": deadline,
        "destination": destination,
        "value": priority * 10,
    }


# ---------------------------------------------------------------------------
# TestSorting
# ---------------------------------------------------------------------------

class TestSorting(unittest.TestCase):
    """Tests for merge sort implementations in algorithms/sorting.py."""

    def setUp(self):
        self.parcels = [
            make_parcel("P001", "Box A", 3.0, 2, "2026-12-15", "Downtown"),
            make_parcel("P002", "Box B", 1.5, 5, "2026-12-05", "Airport"),
            make_parcel("P003", "Box C", 2.0, 1, "2026-12-20", "Mall"),
            make_parcel("P004", "Box D", 4.0, 4, "2026-12-10", "Hospital"),
            make_parcel("P005", "Box E", 2.5, 3, "2026-12-01", "University"),
        ]

    # --- sort_by_priority ---

    def test_sort_by_priority_descending(self):
        """sort_by_priority should return parcels with descending priority."""
        result = sort_by_priority(self.parcels)
        priorities = [p["priority"] for p in result]
        self.assertEqual(priorities, sorted(priorities, reverse=True),
                         "Priorities should be in descending order")

    def test_sort_by_priority_highest_first(self):
        """First parcel after sort should have the highest priority."""
        result = sort_by_priority(self.parcels)
        self.assertEqual(result[0]["priority"], 5)

    def test_sort_by_priority_lowest_last(self):
        """Last parcel after sort should have the lowest priority."""
        result = sort_by_priority(self.parcels)
        self.assertEqual(result[-1]["priority"], 1)

    def test_sort_by_priority_does_not_mutate(self):
        """sort_by_priority should not modify the original list."""
        original = [p.copy() for p in self.parcels]
        sort_by_priority(self.parcels)
        for orig, cur in zip(original, self.parcels):
            self.assertEqual(orig["id"], cur["id"])

    # --- sort_by_deadline ---

    def test_sort_by_deadline_ascending(self):
        """sort_by_deadline should return parcels with ascending deadline."""
        result = sort_by_deadline(self.parcels)
        deadlines = [p["deadline"] for p in result]
        self.assertEqual(deadlines, sorted(deadlines),
                         "Deadlines should be in ascending (earliest-first) order")

    def test_sort_by_deadline_earliest_first(self):
        """First parcel after sort should have the earliest deadline."""
        result = sort_by_deadline(self.parcels)
        self.assertEqual(result[0]["deadline"], "2026-12-01")

    def test_sort_by_deadline_latest_last(self):
        """Last parcel after sort should have the latest deadline."""
        result = sort_by_deadline(self.parcels)
        self.assertEqual(result[-1]["deadline"], "2026-12-20")

    # --- sort_by_combined ---

    def test_sort_by_combined_primary_priority_desc(self):
        """sort_by_combined: primary key is priority descending."""
        # Add two parcels with same priority but different deadlines
        parcels = [
            make_parcel("PA", "A", 1, 3, "2026-12-30", "X"),
            make_parcel("PB", "B", 1, 5, "2026-12-01", "Y"),
            make_parcel("PC", "C", 1, 3, "2026-12-05", "Z"),
        ]
        result = sort_by_combined(parcels)
        # Highest priority comes first
        self.assertEqual(result[0]["priority"], 5)

    def test_sort_by_combined_secondary_deadline_asc(self):
        """sort_by_combined: secondary key is deadline ascending (tie-break)."""
        parcels = [
            make_parcel("PA", "A", 1, 3, "2026-12-30", "X"),
            make_parcel("PB", "B", 1, 3, "2026-12-05", "Z"),
            make_parcel("PC", "C", 1, 3, "2026-12-15", "W"),
        ]
        result = sort_by_combined(parcels)
        deadlines = [p["deadline"] for p in result]
        self.assertEqual(deadlines, sorted(deadlines),
                         "Equal-priority parcels should be sorted by deadline ascending")

    def test_sort_by_combined_length_preserved(self):
        """sort_by_combined should return all parcels."""
        result = sort_by_combined(self.parcels)
        self.assertEqual(len(result), len(self.parcels))


# ---------------------------------------------------------------------------
# TestKnapsack
# ---------------------------------------------------------------------------

class TestKnapsack(unittest.TestCase):
    """
    Tests for 0/1 Knapsack DP in algorithms/knapsack.py.

    Known example:
        3 parcels: weights=[2, 3, 4], priorities=[3, 4, 5]
        Values = priority * 10 → [30, 40, 50]
        Capacity = 5 kg

        Possible selections:
          P1 alone   → value 30, weight 2
          P2 alone   → value 40, weight 3
          P3 alone   → value 50, weight 4
          P1+P2      → value 70, weight 5  ← OPTIMAL
          P1+P3      → value 80, weight 6  (exceeds capacity)
          P2+P3      → value 90, weight 7  (exceeds capacity)

        Optimal: select P1 and P2 → total value 70, total weight 5.
    """

    def setUp(self):
        self.parcels = [
            make_parcel("P001", "Light Box",  2.0, 3, "2026-12-10", "Downtown"),
            make_parcel("P002", "Medium Box", 3.0, 4, "2026-12-15", "Airport"),
            make_parcel("P003", "Heavy Box",  4.0, 5, "2026-12-20", "Mall"),
        ]
        self.capacity = 5.0  # kg

    def test_total_value_is_optimal(self):
        """Optimal value for the known example should be 70."""
        result = knapsack_dp(self.parcels, self.capacity)
        self.assertEqual(result["total_value"], 70,
                         f"Expected total_value=70, got {result['total_value']}")

    def test_selected_count(self):
        """Optimal selection should include exactly 2 parcels."""
        result = knapsack_dp(self.parcels, self.capacity)
        self.assertEqual(len(result["selected"]), 2)

    def test_selected_ids(self):
        """P001 and P002 should be selected (not P003)."""
        result = knapsack_dp(self.parcels, self.capacity)
        selected_ids = {p["id"] for p in result["selected"]}
        self.assertIn("P001", selected_ids)
        self.assertIn("P002", selected_ids)
        self.assertNotIn("P003", selected_ids)

    def test_total_weight_within_capacity(self):
        """Total weight of selected parcels must not exceed capacity."""
        result = knapsack_dp(self.parcels, self.capacity)
        self.assertLessEqual(result["total_weight"], self.capacity)

    def test_rejected_contains_p003(self):
        """P003 should be in the rejected list."""
        result = knapsack_dp(self.parcels, self.capacity)
        rejected_ids = {p["id"] for p in result["rejected"]}
        self.assertIn("P003", rejected_ids)

    def test_result_has_dp_table(self):
        """Result must include a dp_table 2D list."""
        result = knapsack_dp(self.parcels, self.capacity)
        self.assertIn("dp_table", result)
        self.assertIsInstance(result["dp_table"], list)
        self.assertIsInstance(result["dp_table"][0], list)

    def test_result_has_elapsed(self):
        """Result must include elapsed time."""
        result = knapsack_dp(self.parcels, self.capacity)
        self.assertIn("elapsed", result)
        self.assertGreaterEqual(result["elapsed"], 0.0)

    def test_zero_capacity(self):
        """With zero capacity, no parcels should be selected."""
        result = knapsack_dp(self.parcels, 0.0)
        self.assertEqual(result["total_value"], 0)
        self.assertEqual(len(result["selected"]), 0)

    def test_all_fit(self):
        """With large capacity, all parcels should be selected."""
        result = knapsack_dp(self.parcels, 100.0)
        self.assertEqual(len(result["selected"]), 3)


# ---------------------------------------------------------------------------
# TestDijkstra
# ---------------------------------------------------------------------------

class TestDijkstra(unittest.TestCase):
    """
    Tests for Dijkstra's algorithm in algorithms/dijkstra.py.

    Graph (undirected, represented as directed):

        A --4-- B
        |       |
        2       1
        |       |
        C --3-- D --2-- E

        A-C: 2, A-B: 4, C-D: 3, B-D: 1, D-E: 2

    Known shortest distances from A:
        A: 0
        C: 2        (A→C)
        B: 4        (A→B)
        D: 5        (A→C→D)  [not A→B→D which is 5 too — tie]
        E: 7        (A→C→D→E)
    """

    def setUp(self):
        self.graph = {
            "A": {"B": 4, "C": 2},
            "B": {"A": 4, "D": 1},
            "C": {"A": 2, "D": 3},
            "D": {"B": 1, "C": 3, "E": 2},
            "E": {"D": 2},
        }

    def test_distance_to_self_is_zero(self):
        distances, _ = dijkstra(self.graph, "A")
        self.assertEqual(distances["A"], 0)

    def test_distance_to_c(self):
        distances, _ = dijkstra(self.graph, "A")
        self.assertAlmostEqual(distances["C"], 2.0)

    def test_distance_to_b(self):
        distances, _ = dijkstra(self.graph, "A")
        self.assertAlmostEqual(distances["B"], 4.0)

    def test_distance_to_d(self):
        # Optimal: A→B→D = 5 or A→C→D = 5; both are 5
        distances, _ = dijkstra(self.graph, "A")
        self.assertAlmostEqual(distances["D"], 5.0)

    def test_distance_to_e(self):
        distances, _ = dijkstra(self.graph, "A")
        self.assertAlmostEqual(distances["E"], 7.0)

    def test_all_nodes_reachable(self):
        distances, _ = dijkstra(self.graph, "A")
        for node in self.graph:
            self.assertIn(node, distances)
            self.assertLess(distances[node], float("inf"))

    def test_path_a_to_e_is_valid(self):
        """Shortest path A→E should be a connected sequence starting at A ending at E."""
        _, predecessors = dijkstra(self.graph, "A")
        path = get_shortest_path(predecessors, "A", "E")
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "E")

    def test_path_a_to_e_hops(self):
        """Shortest path A→E should have exactly 4 nodes (A, C or B, D, E)."""
        _, predecessors = dijkstra(self.graph, "A")
        path = get_shortest_path(predecessors, "A", "E")
        self.assertEqual(len(path), 4)

    def test_path_continuity(self):
        """Every consecutive pair in the path must be connected by an edge."""
        _, predecessors = dijkstra(self.graph, "A")
        path = get_shortest_path(predecessors, "A", "E")
        for i in range(len(path) - 1):
            self.assertIn(path[i + 1], self.graph[path[i]],
                          f"No edge between {path[i]} and {path[i+1]}")

    def test_single_node_graph(self):
        """Dijkstra on a single-node graph should return distance 0."""
        distances, _ = dijkstra({"A": {}}, "A")
        self.assertEqual(distances["A"], 0)

    def test_path_to_self_is_single_node(self):
        """Path from A to A should be just ['A']."""
        _, predecessors = dijkstra(self.graph, "A")
        path = get_shortest_path(predecessors, "A", "A")
        self.assertEqual(path, ["A"])


# ---------------------------------------------------------------------------
# TestTSP
# ---------------------------------------------------------------------------

class TestTSP(unittest.TestCase):
    """
    Tests for Nearest Neighbor TSP in algorithms/tsp.py.

    5 locations: Warehouse, A, B, C, D
    Distance matrix (symmetric):
              Warehouse  A     B     C     D
    Warehouse    0      2.0   9.0   10.0  5.0
    A            2.0    0     6.0   4.0   8.0
    B            9.0    6.0   0     3.0   7.0
    C            10.0   4.0   3.0   0     1.0
    D            5.0    8.0   7.0   1.0   0

    Nearest Neighbor from Warehouse:
        Start: Warehouse (visited={Warehouse})
        Nearest unvisited: A (dist=2)
        Nearest unvisited from A: C (dist=4)  [B=6, D=8]
        Nearest unvisited from C: D (dist=1)
        Nearest unvisited from D: B (dist=7)
        Return to Warehouse from B: 9
        Route: Warehouse → A → C → D → B → Warehouse
        Total = 2+4+1+7+9 = 23
    """

    def setUp(self):
        self.locations = ["Warehouse", "A", "B", "C", "D"]
        self.distance_matrix = {
            "Warehouse": {"Warehouse": 0, "A": 2.0, "B": 9.0, "C": 10.0, "D": 5.0},
            "A":         {"Warehouse": 2.0, "A": 0, "B": 6.0, "C": 4.0, "D": 8.0},
            "B":         {"Warehouse": 9.0, "A": 6.0, "B": 0, "C": 3.0, "D": 7.0},
            "C":         {"Warehouse": 10.0, "A": 4.0, "B": 3.0, "C": 0, "D": 1.0},
            "D":         {"Warehouse": 5.0, "A": 8.0, "B": 7.0, "C": 1.0, "D": 0},
        }

    def test_route_starts_at_warehouse(self):
        """Route must start at Warehouse."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        self.assertEqual(result["route"][0], "Warehouse")

    def test_route_ends_at_warehouse(self):
        """Route must end at Warehouse (round trip)."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        self.assertEqual(result["route"][-1], "Warehouse")

    def test_all_locations_visited(self):
        """All 5 locations must appear in the route (excluding the return duplicate)."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        visited = set(result["route"])
        for loc in self.locations:
            self.assertIn(loc, visited)

    def test_route_length(self):
        """Route should have 6 entries: 5 locations + return to Warehouse."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        self.assertEqual(len(result["route"]), 6)

    def test_total_distance_is_positive(self):
        """Total distance must be a positive number."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        self.assertGreater(result["total_distance"], 0)

    def test_total_distance_known_value(self):
        """Nearest-neighbor from Warehouse should produce total distance 23."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        self.assertAlmostEqual(result["total_distance"], 23.0, places=5)

    def test_route_segments_present(self):
        """Result must include route_segments list."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        self.assertIn("route_segments", result)
        self.assertIsInstance(result["route_segments"], list)

    def test_route_segments_count(self):
        """Should have 5 segments for a 5-location round trip."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        self.assertEqual(len(result["route_segments"]), 5)

    def test_segment_total_matches_distance(self):
        """Sum of segment distances should equal total_distance."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        segment_total = sum(seg[2] for seg in result["route_segments"])
        self.assertAlmostEqual(segment_total, result["total_distance"], places=5)

    def test_no_location_visited_twice(self):
        """No delivery location should appear twice (Warehouse appears twice as start/end)."""
        result = nearest_neighbor_tsp(self.locations, self.distance_matrix, start="Warehouse")
        # Strip the last Warehouse (return)
        inner_route = result["route"][:-1]
        self.assertEqual(len(inner_route), len(set(inner_route)),
                         "Some location was visited more than once")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
