"""
main.py — Mini-Courier Planner
Streamlit app entry point. Run with:
    cd "/Users/neelanshsahu/Mini-Courier Planner"
    streamlit run main.py
"""

import sys
import os
import json

import streamlit as st
import pandas as pd
import plotly.io as pio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Mini-Courier Planner",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Plotly global template: transparent backgrounds, theme-neutral font ──────
pio.templates["courier"] = pio.templates["plotly"]
pio.templates["courier"].layout.paper_bgcolor = "rgba(0,0,0,0)"
pio.templates["courier"].layout.plot_bgcolor  = "rgba(0,0,0,0)"
pio.templates["courier"].layout.font          = dict(family="Inter, Segoe UI, sans-serif")
pio.templates.default = "courier"

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Mini-Courier Planner",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
        padding: 0.25rem 0;
    }

    /* Main background */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        margin-bottom: 1rem;
    }
    .kpi-card h2 { font-size: 2rem; margin: 0; font-weight: 700; }
    .kpi-card p  { margin: 0; font-size: 0.85rem; opacity: 0.85; }

    /* Section headings — no fixed color so it adapts to light/dark theme */
    .section-header {
        border-left: 4px solid #667eea;
        padding-left: 0.75rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    /* Status badge */
    .badge-done    { background:#27ae60; color:#fff; padding:2px 10px; border-radius:20px; font-size:0.8rem; }
    .badge-pending { background:#e67e22; color:#fff; padding:2px 10px; border-radius:20px; font-size:0.8rem; }

    /* Metric box — use semi-transparent background that works on both themes */
    div[data-testid="metric-container"] {
        background: rgba(102, 126, 234, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.25);
        border-radius: 10px;
        padding: 0.8rem;
    }

    /* Table row coloring handled inline via pandas styler */

    /* Button */
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state initialisation ─────────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))


def _normalise_parcel(row: dict) -> dict:
    """Coerce a raw CSV/upload row into the standard parcel schema."""
    priority = int(row.get("priority", 1))
    return {
        "id":          str(row.get("id", "P000")),
        "name":        str(row.get("name", "Unknown")),
        "weight":      float(row.get("weight", 0.0)),
        "priority":    priority,
        "deadline":    str(row.get("deadline", "2026-12-31")),
        "destination": str(row.get("destination", "Warehouse")),
        "value":       float(row.get("value", priority * 10)),
    }


def _load_default_parcels() -> list:
    csv_path = os.path.join(_BASE, "data", "sample_parcels.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return [_normalise_parcel(r) for r in df.to_dict("records")]
    return []


def _load_default_locations() -> dict:
    json_path = os.path.join(_BASE, "data", "sample_locations.json")
    if os.path.exists(json_path):
        with open(json_path) as f:
            return json.load(f)
    return {"nodes": [], "edges": []}


if "parcels" not in st.session_state:
    st.session_state.parcels = _load_default_parcels()

if "vehicle_capacity" not in st.session_state:
    st.session_state.vehicle_capacity = 50.0

if "knapsack_result" not in st.session_state:
    st.session_state.knapsack_result = None

if "route_result" not in st.session_state:
    st.session_state.route_result = None

if "performance_data" not in st.session_state:
    _perf_path = os.path.join(_BASE, "results", "performance_results.json")
    if os.path.exists(_perf_path):
        with open(_perf_path) as f:
            try:
                st.session_state.performance_data = json.load(f)
            except Exception:
                st.session_state.performance_data = {}
    else:
        st.session_state.performance_data = {}

if "locations_data" not in st.session_state:
    st.session_state.locations_data = _load_default_locations()

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.markdown("## 🚚 Mini-Courier Planner")
st.sidebar.markdown("---")

PAGES = [
    "🏠 Overview",
    "📦 Parcel Management",
    "⚙️ Parcel Optimization",
    "🗺️ Route Optimization",
    "📊 Performance Analytics",
    "🏁 Final Delivery Results",
]

page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"**Parcels loaded:** {len(st.session_state.parcels)}  \n"
    f"**Capacity:** {st.session_state.vehicle_capacity} kg  \n"
    f"**Knapsack:** {'✅' if st.session_state.knapsack_result else '⏳'}  \n"
    f"**Route:** {'✅' if st.session_state.route_result else '⏳'}"
)

# ── Page routing ──────────────────────────────────────────────────────────────
state = st.session_state

if page == "🏠 Overview":
    from dashboard.overview import show_overview
    show_overview(state)

elif page == "📦 Parcel Management":
    from dashboard.parcel_management import show_parcel_management
    show_parcel_management(state)

elif page == "⚙️ Parcel Optimization":
    from dashboard.parcel_optimization import show_parcel_optimization
    show_parcel_optimization(state)

elif page == "🗺️ Route Optimization":
    from dashboard.route_optimization import show_route_optimization
    show_route_optimization(state)

elif page == "📊 Performance Analytics":
    from dashboard.performance_analytics import show_performance_analytics
    show_performance_analytics(state)

elif page == "🏁 Final Delivery Results":
    from dashboard.final_results import show_final_results
    show_final_results(state)
