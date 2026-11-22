# 🚚 Mini-Courier Planner — Team Project Documentation

An intelligent courier management and delivery optimization system built collaboratively by a **3-member team** using pure-Python Data Structures & Algorithms and an interactive **Streamlit** dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit&logoColor=white)
![Team](https://img.shields.io/badge/Team-3%20Members-blueviolet)
![Tests](https://img.shields.io/badge/Tests-40%2F40%20Passed-brightgreen)

---

## 👥 Team Members & Division of Work

| Member | Role | Core Ownership | Files Owned |
|--------|------|----------------|-------------|
| **Anjali Rathore** | Parcel Management & Optimization Lead | Merge Sort, 0/1 Knapsack DP, Parcel CRUD, Sample Datasets | `algorithms/sorting.py`, `algorithms/knapsack.py`, `modules/parcel_manager.py`, `data/sample_parcels*.csv` |
| **Neelansh Sahu** | Graph & Route Optimization Lead | Dijkstra's Algorithm, Nearest Neighbor TSP + 2-opt, Route Manager, City Road Graph | `algorithms/dijkstra.py`, `algorithms/tsp.py`, `modules/route_manager.py`, `data/sample_locations.json` |
| **Manav** | Dashboard, Integration & QA Lead | 6-Page Streamlit UI, App Integration, 40 Unit Tests, Performance Benchmarking | `main.py`, `dashboard/*.py`, `testing/test_algorithms.py`, `testing/performance_analysis.py` |

---

## 🧩 Detailed Member Contributions

### 1️⃣ Member 1 — Parcel Management & Optimization
Responsible for all parcel data handling, sorting, and optimal vehicle loading:
- **Merge Sort (`algorithms/sorting.py`)**: Implemented a stable O(n log n) Merge Sort from scratch supporting three sorting modes — priority (descending), deadline (ascending), and combined (priority then deadline).
- **0/1 Knapsack DP (`algorithms/knapsack.py`)**: Implemented dynamic programming to maximize total parcel value (`priority × 10`) within vehicle weight capacity, scaling decimal weights by ×10 for integer DP indexing and returning the full DP table for visualization.
- **Parcel Manager (`modules/parcel_manager.py`)**: Built complete CRUD operations (add, edit, delete, lookup) and CSV import/export logic.
- **Sample Datasets (`data/sample_parcels*.csv`)**: Curated three benchmark datasets — Small (15 parcels), Medium (30 parcels), and Large (60 parcels).

### 2️⃣ Member 2 — Graph & Route Optimization
Responsible for city network modeling, shortest-path computation, and delivery routing:
- **Dijkstra's Algorithm (`algorithms/dijkstra.py`)**: Implemented weighted shortest-path search using Python's `heapq` min-heap in O((V + E) log V), plus path reconstruction and all-pairs shortest-path distance matrix generation.
- **TSP Approximation (`algorithms/tsp.py`)**: Implemented the Nearest Neighbor heuristic followed by **2-opt** local search optimization to produce short round-trip delivery routes starting and ending at `Warehouse`.
- **Route Manager (`modules/route_manager.py`)**: Connected the road graph, Dijkstra distance matrix, and TSP solver into a single routing pipeline with segment-by-segment distance tracking.
- **Location Network (`data/sample_locations.json`)**: Designed the 12-node, 30-edge weighted city road graph connecting the Warehouse to 11 delivery zones.

### 3️⃣ Member 3 — Integration, Dashboard & Testing
Responsible for bringing both algorithmic modules together into a polished web app and verifying correctness and speed:
- **Main Application (`main.py`)**: Built the Streamlit entry point, shared `st.session_state` workflow pipeline, sidebar navigation, and light/dark theme styling.
- **6-Page Interactive Dashboard (`dashboard/`)**:
  - `overview.py` — KPIs, workflow status tracker, and priority charts
  - `parcel_management.py` — CSV upload, sample loader, manual entry, and edit/delete forms
  - `parcel_optimization.py` — Sorting interface, Knapsack runner, and DP table heatmap
  - `route_optimization.py` — Interactive city network graph, Dijkstra explorer, and TSP route visualizer
  - `performance_analytics.py` — Live algorithm timing benchmarks and complexity curves
  - `final_results.py` — Consolidated delivery plan and CSV/JSON export
- **Testing & Benchmarks (`testing/`)**: Wrote 40 automated unit tests (`test_algorithms.py`) covering all four algorithms and built the timing benchmark suite (`performance_analysis.py`).

---

## 🔗 System Integration Architecture

```text
┌─────────────────────────────────────┐
│        Member 1: Parcel Layer       │
│  CSV / CRUD → Merge Sort → Knapsack │
└──────────────────┬──────────────────┘
                   │ Selected Parcels & Destinations
                   ▼
┌─────────────────────────────────────┐
│        Member 2: Route Layer        │
│  Road Graph → Dijkstra → TSP + 2opt │
└──────────────────┬──────────────────┘
                   │ Optimized Route & Distances
                   ▼
┌─────────────────────────────────────┐
│     Member 3: Dashboard & QA Layer  │
│  Streamlit UI → Analytics → Export  │
└─────────────────────────────────────┘
```

---

## 🗂️ Project Structure by Ownership

```text
Mini-Courier Planner/
├── main.py                        # [Member 3] Application entry point & session state
├── requirements.txt               # [Member 3] Dependencies
├── algorithms/
│   ├── sorting.py                 # [Member 1] Merge Sort
│   ├── knapsack.py                # [Member 1] 0/1 Knapsack DP
│   ├── dijkstra.py                # [Member 2] Dijkstra's shortest path
│   └── tsp.py                     # [Member 2] Nearest Neighbor TSP + 2-opt
├── modules/
│   ├── parcel_manager.py          # [Member 1] Parcel CRUD & CSV I/O
│   └── route_manager.py           # [Member 2] Graph loader & route planner
├── dashboard/                     # [Member 3] 6-page Streamlit UI
│   ├── overview.py
│   ├── parcel_management.py
│   ├── parcel_optimization.py
│   ├── route_optimization.py
│   ├── performance_analytics.py
│   └── final_results.py
├── data/
│   ├── sample_parcels.csv         # [Member 1] 15 parcels
│   ├── sample_parcels_medium.csv  # [Member 1] 30 parcels
│   ├── sample_parcels_large.csv   # [Member 1] 60 parcels
│   └── sample_locations.json      # [Member 2] 12-node city road network
└── testing/                       # [Member 3] Verification & benchmarking
    ├── test_algorithms.py         # 40 unit tests
    └── performance_analysis.py    # Benchmark script
```

---

## 🚀 How to Run

```bash
git clone https://github.com/neelanshsahu/Mini-Courier-Planner.git
cd Mini-Courier-Planner
pip install -r requirements.txt
streamlit run main.py
```

### Run Tests & Benchmarks

```bash
python -m pytest testing/test_algorithms.py -v
python testing/performance_analysis.py
```

---

## ✅ Verification Summary

| Component | Owner | Result |
|-----------|-------|--------|
| Merge Sort & 0/1 Knapsack | Member 1 | 19/19 unit tests passed |
| Dijkstra & TSP + 2-opt | Member 2 | 21/21 unit tests passed |
| Full Pipeline & 6-Page Dashboard | Member 3 | End-to-end verified (40/40 total tests passed) |
