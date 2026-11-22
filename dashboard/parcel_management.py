"""
dashboard/parcel_management.py — Parcel Management page.
"""

import os
import sys
import io

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.parcel_manager import ParcelManager

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CSV_MAP = {
    "Small (15 parcels)":  os.path.join(_BASE, "data", "sample_parcels.csv"),
    "Medium (30 parcels)": os.path.join(_BASE, "data", "sample_parcels_medium.csv"),
    "Large (60 parcels)":  os.path.join(_BASE, "data", "sample_parcels_large.csv"),
}

PRIORITY_COLORS = {1: "#e74c3c", 2: "#e67e22", 3: "#f1c40f", 4: "#2ecc71", 5: "#27ae60"}
DESTINATIONS = [
    "Downtown", "Airport", "Mall", "Hospital", "University",
    "Station", "Harbor", "Tech Park", "Old Town",
    "Suburb North", "Suburb South",
]


def _normalise_parcel(row: dict) -> dict:
    """Coerce any raw dict into the canonical parcel schema."""
    priority = int(float(row.get("priority", 1) or 1))
    return {
        "id":          str(row.get("id", "P000")).strip(),
        "name":        str(row.get("name", "Unknown")).strip(),
        "weight":      float(row.get("weight", 0.0) or 0.0),
        "priority":    priority,
        "deadline":    str(row.get("deadline", "2026-12-31")).strip(),
        "destination": str(row.get("destination", "Warehouse")).strip(),
        "value":       float(row.get("value", priority * 10) or priority * 10),
    }


def _highlight_priority(val):
    colors = {1: "#ffd6d6", 2: "#ffeacc", 3: "#fff9c4", 4: "#d4f7d4", 5: "#b8f0b8"}
    return f"background-color: {colors.get(val, '#fff')}; color: #000"


def _get_manager(state) -> ParcelManager:
    pm = ParcelManager()
    pm.parcels = list(state.parcels)
    return pm


def show_parcel_management(state):
    st.markdown("<h2 class='section-header'>📦 Parcel Management</h2>", unsafe_allow_html=True)

    # ── Section 1: Load Data ─────────────────────────────────────────────────
    st.markdown("### 1️⃣ Load Parcel Data")
    load_tab1, load_tab2, load_tab3 = st.tabs(["📂 Upload CSV", "📋 Load Sample", "✏️ Manual Entry"])

    with load_tab1:
        uploaded = st.file_uploader("Upload a parcel CSV file", type=["csv"])
        if uploaded is not None:
            try:
                df_up = pd.read_csv(uploaded)
                state.parcels = [_normalise_parcel(r) for r in df_up.to_dict("records")]
                state.knapsack_result = None
                state.route_result = None
                st.success(f"✅ Loaded {len(state.parcels)} parcels from uploaded file.")
            except Exception as e:
                st.error(f"Failed to read CSV: {e}")

    with load_tab2:
        sample_choice = st.selectbox("Choose sample dataset", list(_CSV_MAP.keys()))
        if st.button("Load Sample Dataset"):
            csv_path = _CSV_MAP[sample_choice]
            if os.path.exists(csv_path):
                df_s = pd.read_csv(csv_path)
                state.parcels = [_normalise_parcel(r) for r in df_s.to_dict("records")]
                state.knapsack_result = None
                state.route_result = None
                st.success(f"✅ Loaded {len(state.parcels)} parcels from {sample_choice}.")
            else:
                st.error(f"File not found: {csv_path}")

    with load_tab3:
        with st.form("manual_add_form"):
            st.markdown("**Add a new parcel manually**")
            c1, c2 = st.columns(2)
            with c1:
                p_name   = st.text_input("Parcel name", value="New Parcel")
                p_weight = st.number_input("Weight (kg)", min_value=0.1, max_value=500.0, value=2.0, step=0.1)
                p_prio   = st.slider("Priority (1=low, 5=high)", 1, 5, 3)
            with c2:
                p_dead   = st.date_input("Deadline")
                p_dest   = st.selectbox("Destination", DESTINATIONS)
            submitted = st.form_submit_button("➕ Add Parcel")
            if submitted:
                pm = _get_manager(state)
                pm.add_parcel(
                    name=p_name,
                    weight=p_weight,
                    priority=p_prio,
                    deadline=str(p_dead),
                    destination=p_dest,
                )
                state.parcels = pm.get_all_parcels()
                st.success(f"✅ Added parcel '{p_name}'.")

    st.markdown("---")

    # ── Vehicle capacity ─────────────────────────────────────────────────────
    st.markdown("### ⚖️ Vehicle Settings")
    state.vehicle_capacity = st.number_input(
        "Vehicle capacity (kg)",
        min_value=1.0, max_value=500.0,
        value=float(state.vehicle_capacity),
        step=1.0,
        help="Maximum weight the vehicle can carry — used for Knapsack optimization.",
    )

    st.markdown("---")

    # ── Section 2: Parcel Table ───────────────────────────────────────────────
    st.markdown("### 2️⃣ Current Parcels")

    parcels = getattr(state, "parcels", [])
    if not parcels:
        st.info("No parcels loaded yet. Use the section above to load data.")
        return

    df = pd.DataFrame(parcels)

    # Ensure expected numeric columns exist before computing metrics
    for col, default in [("weight", 0.0), ("priority", 1), ("value", 0.0)]:
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Parcels",     len(df))
    m2.metric("Total Weight (kg)", f"{df['weight'].sum():.2f}")
    m3.metric("Avg Priority",      f"{df['priority'].mean():.2f}")
    m4.metric("Avg Weight (kg)",   f"{df['weight'].mean():.2f}")

    display_cols = [c for c in ["id","name","weight","priority","deadline","destination","value"] if c in df.columns]
    display_df = df[display_cols].copy()
    # Round floats for clean display
    for fc in ["weight", "value"]:
        if fc in display_df.columns:
            display_df[fc] = display_df[fc].round(2)
    if "priority" in display_df.columns:
        display_df["priority"] = display_df["priority"].astype(int)
        styled = display_df.style.map(_highlight_priority, subset=["priority"])
    else:
        styled = display_df.style
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Section 3: Edit / Delete ─────────────────────────────────────────────
    st.markdown("### 3️⃣ Edit or Delete a Parcel")

    if not parcels:
        return

    ids = [p["id"] for p in parcels]
    sel_id = st.selectbox("Select Parcel ID", ids)
    pm = _get_manager(state)
    parcel = pm.get_parcel_by_id(sel_id)

    if parcel:
        with st.form("edit_form"):
            st.markdown(f"**Editing: {parcel['id']} — {parcel['name']}**")
            ec1, ec2 = st.columns(2)
            with ec1:
                e_name   = st.text_input("Name",   value=parcel["name"])
                e_weight = st.number_input("Weight (kg)", min_value=0.1, max_value=500.0,
                                          value=max(0.1, float(parcel["weight"])), step=0.1)
                e_prio   = st.slider("Priority", 1, 5, int(parcel["priority"]))
            with ec2:
                import datetime
                try:
                    dd = datetime.date.fromisoformat(parcel["deadline"])
                except Exception:
                    dd = datetime.date.today()
                e_dead = st.date_input("Deadline", value=dd)
                e_dest = st.selectbox("Destination", DESTINATIONS,
                                      index=DESTINATIONS.index(parcel["destination"])
                                      if parcel["destination"] in DESTINATIONS else 0)

            col_save, col_del = st.columns([3, 1])
            with col_save:
                save = st.form_submit_button("💾 Save Changes")
            with col_del:
                delete = st.form_submit_button("🗑️ Delete Parcel", type="secondary")

            if save:
                pm.edit_parcel(sel_id, name=e_name, weight=e_weight,
                               priority=e_prio, deadline=str(e_dead), destination=e_dest)
                state.parcels = pm.get_all_parcels()
                state.knapsack_result = None
                st.success(f"✅ Parcel {sel_id} updated.")

            if delete:
                pm.delete_parcel(sel_id)
                state.parcels = pm.get_all_parcels()
                state.knapsack_result = None
                st.success(f"🗑️ Parcel {sel_id} deleted.")
