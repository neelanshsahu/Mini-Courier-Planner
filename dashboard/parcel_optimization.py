"""
dashboard/parcel_optimization.py — Parcel Optimization page.
"""

import os
import sys

import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algorithms.sorting import sort_by_priority, sort_by_deadline, sort_by_combined, time_sort
from algorithms.knapsack import knapsack_dp


def show_parcel_optimization(state):
    st.markdown("<h2 class='section-header'>⚙️ Parcel Optimization</h2>", unsafe_allow_html=True)

    parcels = list(getattr(state, "parcels", []))
    if not parcels:
        st.info("👈 No parcels loaded. Go to **📦 Parcel Management** first.")
        return

    # ── Section 1: Sorting ───────────────────────────────────────────────────
    st.markdown("### 1️⃣ Sorting")
    sort_choice = st.selectbox(
        "Sort parcels by:",
        ["Priority (descending)", "Deadline (ascending)", "Combined (priority then deadline)"],
    )

    sort_fn_map = {
        "Priority (descending)":                     sort_by_priority,
        "Deadline (ascending)":                      sort_by_deadline,
        "Combined (priority then deadline)":         sort_by_combined,
    }
    sort_fn = sort_fn_map[sort_choice]

    sorted_list, elapsed = time_sort(parcels, sort_fn)

    st.success(f"✅ Sorted {len(sorted_list)} parcels in **{elapsed*1000:.4f} ms**")

    df_sorted = pd.DataFrame(sorted_list)
    for fc in ["weight", "value"]:
        if fc in df_sorted.columns:
            df_sorted[fc] = df_sorted[fc].round(2)
    if "priority" in df_sorted.columns:
        df_sorted["priority"] = df_sorted["priority"].astype(int)

    def _color_priority(val):
        colors = {1: "#ffd6d6", 2: "#ffeacc", 3: "#fff9c4", 4: "#d4f7d4", 5: "#b8f0b8"}
        return f"background-color: {colors.get(val, '#fff')}; color: #000"

    styled = df_sorted.style.map(_color_priority, subset=["priority"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.info("**Time Complexity:** O(n log n)  \n**Space Complexity:** O(n)")
    with info_col2:
        st.info(f"**Algorithm:** Merge Sort  \n**Input size:** {len(parcels)} parcels")

    st.markdown("---")

    # ── Section 2: Knapsack Optimization ────────────────────────────────────
    st.markdown("### 2️⃣ Knapsack Optimization (0/1 DP)")

    capacity = float(getattr(state, "vehicle_capacity", 50.0))
    st.markdown(
        f"**Vehicle capacity:** `{capacity} kg`   "
        f"&nbsp; *Change in 📦 Parcel Management*",
        unsafe_allow_html=True,
    )

    if st.button("🚀 Run Knapsack Optimization"):
        with st.spinner("Running dynamic programming…"):
            result = knapsack_dp(parcels, capacity)
        state.knapsack_result = result
        st.success(
            f"✅ Optimization complete in **{result['elapsed']*1000:.4f} ms** — "
            f"selected **{len(result['selected'])}** parcels, "
            f"total value **{result['total_value']}**, "
            f"total weight **{result['total_weight']:.2f} kg**"
        )

    result = getattr(state, "knapsack_result", None)
    if not result:
        st.info("Click **Run Knapsack Optimization** to see results.")
        return

    # Result summary metrics
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Selected Parcels",  len(result["selected"]))
    r2.metric("Rejected Parcels",  len(result["rejected"]))
    r3.metric("Total Value",       result["total_value"])
    r4.metric("Total Weight (kg)", f"{result['total_weight']:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Two-column selected / rejected tables
    tc1, tc2 = st.columns(2)
    with tc1:
        st.markdown("#### ✅ Selected Parcels")
        if result["selected"]:
            df_sel = pd.DataFrame(result["selected"])[["id", "name", "weight", "priority", "deadline", "destination"]]
            df_sel["weight"] = df_sel["weight"].round(2)
            df_sel["priority"] = df_sel["priority"].astype(int)
            st.dataframe(
                df_sel.style.set_properties(**{"background-color": "#d4f7d4", "color": "#000"}),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No parcels selected.")

    with tc2:
        st.markdown("#### ❌ Rejected Parcels")
        if result["rejected"]:
            df_rej = pd.DataFrame(result["rejected"])[["id", "name", "weight", "priority", "deadline", "destination"]]
            df_rej["weight"] = df_rej["weight"].round(2)
            df_rej["priority"] = df_rej["priority"].astype(int)
            st.dataframe(
                df_rej.style.set_properties(**{"background-color": "#ffd6d6", "color": "#000"}),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No rejected parcels.")

    st.markdown("<br>", unsafe_allow_html=True)

    # DP table heatmap
    st.markdown("#### 🔥 DP Table Heatmap")
    dp_table = result.get("dp_table", [])
    if dp_table and len(dp_table) > 1:
        # Limit display size for readability
        max_rows = min(len(dp_table), 20)
        max_cols = min(len(dp_table[0]), 60)
        display_table = [row[:max_cols] for row in dp_table[:max_rows]]

        fig_dp = px.imshow(
            display_table,
            title=f"DP Table (rows=items 0–{max_rows-1}, cols=capacity 0–{max_cols-1})",
            color_continuous_scale="Viridis",
            labels={"x": "Capacity (×0.1 kg)", "y": "Item index", "color": "Value"},
            aspect="auto",
        )
        fig_dp.update_layout(
            coloraxis_colorbar=dict(title="Value"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_dp, use_container_width=True)
        if len(dp_table) > 20 or len(dp_table[0]) > 60:
            st.caption(f"Note: Showing first {max_rows} rows × {max_cols} columns of full "
                       f"{len(dp_table)} × {len(dp_table[0])} DP table.")
    else:
        st.info("DP table not available (too few items or zero capacity).")

    # Complexity info
    st.markdown(
        "> **Time Complexity:** O(n × W) &nbsp;|&nbsp; "
        "**Space Complexity:** O(n × W) &nbsp;|&nbsp; "
        "where n = number of parcels, W = capacity (integer units)",
        unsafe_allow_html=True,
    )
