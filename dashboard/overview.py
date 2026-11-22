"""
dashboard/overview.py — Overview page for Mini-Courier Planner.
"""

import streamlit as st
import plotly.express as px
import pandas as pd


def show_overview(state):
    # Hero
    st.markdown(
        """
        <div style='text-align:center; padding: 1.5rem 0 1rem 0;'>
            <h1 style='font-size:2.6rem; margin-bottom:0.2rem;'>
                🚚 Mini-Courier Planner
            </h1>
            <p style='font-size:1.1rem; opacity:0.7; margin:0;'>
                Intelligent parcel sorting, knapsack optimization &amp; route planning
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── KPI cards ────────────────────────────────────────────────────────────
    parcels = list(getattr(state, "parcels", []))
    knapsack = getattr(state, "knapsack_result", None)
    route    = getattr(state, "route_result", None)

    n_parcels  = len(parcels)
    n_selected = len(knapsack["selected"]) if knapsack else 0
    total_dist = f"{route['total_distance']:.1f} km" if route else "—"
    opt_status = "Complete" if (knapsack and route) else ("Partial" if (knapsack or route) else "Pending")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"<div class='kpi-card'><h2>{n_parcels}</h2><p>Total Parcels</p></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='kpi-card'><h2>{n_selected}</h2><p>Selected for Delivery</p></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div class='kpi-card'><h2>{total_dist}</h2><p>Total Route Distance</p></div>",
            unsafe_allow_html=True,
        )
    with c4:
        badge_cls = "badge-done" if opt_status == "Complete" else "badge-pending"
        st.markdown(
            f"<div class='kpi-card'>"
            f"<h2><span class='{badge_cls}'>{opt_status}</span></h2>"
            f"<p>Optimization Status</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Workflow progress ────────────────────────────────────────────────────
    st.markdown("<h3 class='section-header'>Workflow Progress</h3>", unsafe_allow_html=True)

    steps = [
        ("Load Parcels",        bool(parcels)),
        ("Run Knapsack",        bool(knapsack)),
        ("Plan Route",          bool(route)),
        ("View Final Results",  bool(knapsack and route)),
    ]

    prog_cols = st.columns(len(steps))
    for col, (label, done) in zip(prog_cols, steps):
        with col:
            icon  = "✅" if done else "⏳"
            border_color = "#27ae60" if done else "rgba(128,128,128,0.4)"
            icon_color   = "#27ae60" if done else "inherit"
            st.markdown(
                f"<div style='text-align:center; padding:0.6rem; border-radius:10px;"
                f"border:2px solid {border_color};'>"
                f"<div style='font-size:1.5rem;'>{icon}</div>"
                f"<div style='font-size:0.8rem; color:{icon_color}; font-weight:600;'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick summary table ──────────────────────────────────────────────────
    st.markdown("<h3 class='section-header'>Session Summary</h3>", unsafe_allow_html=True)
    summary = {
        "Item": ["Parcels loaded", "Vehicle capacity", "Knapsack optimized", "Route planned"],
        "Status": [
            str(n_parcels),
            f"{getattr(state, 'vehicle_capacity', 50.0)} kg",
            f"Yes — {n_selected} selected" if knapsack else "No",
            f"Yes — {total_dist}" if route else "No",
        ],
    }
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    if not parcels:
        st.info("👈 No parcels loaded yet. Go to **📦 Parcel Management** to load data.")
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ───────────────────────────────────────────────────────────────
    df = pd.DataFrame(parcels)

    left, right = st.columns(2)

    with left:
        st.markdown("<h4>Weight Distribution</h4>", unsafe_allow_html=True)
        fig_w = px.histogram(
            df, x="weight", nbins=10,
            title="Parcel Weight Distribution",
            labels={"weight": "Weight (kg)", "count": "Count"},
            color_discrete_sequence=["#667eea"],
        )
        fig_w.update_layout(bargap=0.1)
        st.plotly_chart(fig_w, use_container_width=True)

    with right:
        st.markdown("<h4>Priority Distribution</h4>", unsafe_allow_html=True)
        priority_counts = df["priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Count"]
        priority_counts = priority_counts.sort_values("Priority")
        fig_p = px.pie(
            priority_counts, values="Count", names="Priority",
            title="Priority Breakdown",
            color_discrete_sequence=px.colors.sequential.Viridis,
        )
        fig_p.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_p, use_container_width=True)
