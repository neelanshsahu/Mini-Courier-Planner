# 🚚 Mini-Courier Planner

An interactive courier management and delivery optimization web application built with **Python** and **Streamlit**. Plan optimal parcel loads, calculate shortest city routes, and visualize delivery performance using classic Data Structures & Algorithms implemented from scratch.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-40%2F40%20Passed-brightgreen)

---

## ✨ Features

- **Parcel Management** — Upload custom CSV files, load built-in sample datasets (15, 30, or 60 parcels), or add, edit, and delete parcels manually.
- **Smart Parcel Sorting** — Sort parcels by priority, deadline, or a combined priority-then-deadline order using **Merge Sort**.
- **Optimal Vehicle Packing** — Maximize total delivery value within your vehicle's weight capacity using **0/1 Knapsack Dynamic Programming**, complete with an interactive DP table heatmap.
- **Shortest Path & Route Planning** — Explore the 12-location city road network, find point-to-point shortest paths with **Dijkstra's Algorithm**, and generate optimized round-trip delivery routes from the Warehouse using **Nearest Neighbor TSP + 2-opt**.
- **Performance Analytics** — Benchmark all four algorithms across varying input sizes and inspect execution-time growth curves.
- **Exportable Delivery Plans** — Review the final selected parcels, delivery sequence, and capacity utilization, then export the plan as **CSV** or **JSON**.
- **Light & Dark Theme Support** — All tables and Plotly charts adapt cleanly to Streamlit's light and dark themes.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- `pip`

### Installation & Launch

```bash
# 1. Clone the repository
git clone https://github.com/neelanshsahu/Mini-Courier-Planner.git
cd Mini-Courier-Planner

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the application
streamlit run main.py
```

Open your browser to **http://localhost:8501**.

---

## 📖 How to Use

Follow the 6 pages in the sidebar from top to bottom:

1. **🏠 Overview**  
   View high-level metrics (loaded parcels, vehicle capacity, optimization status), workflow progress, and priority distribution charts.

2. **📦 Parcel Management**  
   - Load a sample dataset (`Small 15`, `Medium 30`, or `Large 60`), upload your own CSV, or add parcels manually.
   - Edit or delete existing parcels.
   - Set your **Vehicle Capacity (kg)** (default: `50.0 kg`).

3. **⚙️ Parcel Optimization**  
   - Sort parcels by priority, deadline, or combined criteria.
   - Click **Run Knapsack Optimization** to select the highest-value parcel subset that fits within the vehicle's weight limit.
   - Inspect selected vs. rejected parcels and the DP table heatmap.

4. **🗺️ Route Optimization**  
   - View the interactive 12-node city network map.
   - Use **Dijkstra's Algorithm** to find the shortest path between any two locations.
   - Destinations from your Knapsack result are pre-selected automatically; click **Run Route Optimization** to generate the shortest round-trip route starting and ending at `Warehouse` (with optional 2-opt refinement).

5. **📊 Performance Analytics**  
   Run live benchmarks to compare execution times of Merge Sort, Knapsack DP, Dijkstra, and TSP across increasing dataset/graph sizes.

6. **🏁 Final Delivery Results**  
   Review the complete delivery summary, segment-by-segment route breakdown, and download the final plan in **CSV** or **JSON** format.

### Custom CSV Format

When uploading your own parcel CSV, use the following columns:

```csv
id,name,weight,priority,deadline,destination
P001,Electronics Package,3.5,5,2026-12-01,Downtown
P002,Medical Supplies,1.2,5,2026-12-02,Hospital
```

- `priority`: integer from `1` (lowest) to `5` (highest). Parcel value is calculated as `priority × 10`.
- `destination`: must match one of the 11 delivery locations (`Downtown`, `Airport`, `Mall`, `Hospital`, `University`, `Station`, `Harbor`, `Tech Park`, `Old Town`, `Suburb North`, `Suburb South`).

---

## 🧠 Algorithms Under the Hood

All algorithms are hand-coded in pure Python without external algorithm libraries:

| Algorithm | Module | Purpose | Time Complexity | Space Complexity |
|-----------|--------|---------|-----------------|------------------|
| **Merge Sort** | `algorithms/sorting.py` | Stable parcel sorting (priority / deadline / combined) | O(n log n) | O(n) |
| **0/1 Knapsack DP** | `algorithms/knapsack.py` | Optimal parcel selection within weight capacity | O(n × W) | O(n × W) |
| **Dijkstra's Algorithm** | `algorithms/dijkstra.py` | Weighted shortest paths & all-pairs distance matrix | O((V + E) log V) | O(V + E) |
| **Nearest Neighbor + 2-opt** | `algorithms/tsp.py` | Delivery route ordering & local swap optimization | O(n²) | O(n) |

---

## 🗂️ Project Structure

```text
Mini-Courier Planner/
├── main.py                        # Streamlit application entry point
├── requirements.txt               # Python dependencies
├── algorithms/                    # Pure-Python DSA implementations
│   ├── sorting.py                 # Merge Sort
│   ├── knapsack.py                # 0/1 Knapsack DP
│   ├── dijkstra.py                # Dijkstra's shortest path
│   └── tsp.py                     # Nearest Neighbor TSP + 2-opt
├── modules/                       # Core business logic
│   ├── parcel_manager.py          # Parcel CRUD & CSV handling
│   └── route_manager.py           # Graph loading & route planning
├── dashboard/                     # Streamlit UI pages
│   ├── overview.py
│   ├── parcel_management.py
│   ├── parcel_optimization.py
│   ├── route_optimization.py
│   ├── performance_analytics.py
│   └── final_results.py
├── data/                          # Sample datasets & city road graph
│   ├── sample_parcels.csv         # 15 parcels
│   ├── sample_parcels_medium.csv  # 30 parcels
│   ├── sample_parcels_large.csv   # 60 parcels
│   └── sample_locations.json      # 12 locations, 30 weighted edges
├── testing/                       # Unit tests & benchmarks
│   ├── test_algorithms.py         # 40 unit tests
│   └── performance_analysis.py    # Benchmark runner
└── results/
    └── performance_results.json   # Generated benchmark output
```

---

## ✅ Testing & Benchmarks

```bash
# Run all 40 unit tests
python -m pytest testing/test_algorithms.py -v

# Run performance benchmarks
python testing/performance_analysis.py
```

---

## 🔧 Tech Stack

- **Python 3.10+** — Core logic and hand-coded algorithms
- **Streamlit** — Interactive multi-page web interface
- **Pandas** — Tabular data handling and CSV I/O
- **Plotly** — Interactive network maps, heatmaps, and charts
- **pytest** — Automated unit testing
