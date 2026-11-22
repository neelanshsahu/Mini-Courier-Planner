"""
dashboard/final_results.py — Final Delivery Results page.
"""

import os
import sys
import io
import json
import csv

import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_final_results(state):
    st.markdown("<h2 class='section-header'>🏁 Final Delivery Results</h2>", unsafe_allow_html=True)

    knapsack = getattr(state, "knapsack_result", None)
    route    = getattr(state, "route_result", None)

    # Guard: warn if steps not completed
    if not knapsack and not route:
        st.warning(
            "⚠️ Neither Knapsack Optimization nor Route Planning has been run yet.\n\n"
            "Please complete the following steps first:\n"
            "1. **📦 Parcel Management** — load your parcels\n"
            "2. **⚙️ Parcel Optimization** — run Knapsack optimization\n"
            "3. **🗺️ Route Optimization** — plan the delivery route"
        )
        return

    if not knapsack:
        st.warning("⚠️ Knapsack Optimization not yet run. Go to **⚙️ Parcel Optimization**.")
    if not route:
        st.warning("⚠️ Route not yet planned. Go to **🗺️ Route Optimization**.")

    # ── Top-level metrics ────────────────────────────────────────────────────
    st.markdown("### 📊 Delivery Summary")

    n_delivered  = len(knapsack["selected"])  if knapsack else 0
    n_rejected   = len(knapsack["rejected"])  if knapsack else 0
    total_weight = knapsack["total_weight"]   if knapsack else 0.0
    total_value  = knapsack["total_value"]    if knapsack else 0
    total_dist   = route["total_distance"]    if route else 0.0
    n_stops      = len(route["route"]) - 2    if route else 0  # exclude Warehouse ×2

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Parcels Delivered",    n_delivered)
    m2.metric("Parcels Rejected",     n_rejected)
    m3.metric("Total Weight (kg)",    f"{total_weight:.2f}")
    m4.metric("Total Value",          total_value)
    m5.metric("Total Distance (km)",  f"{total_dist:.2f}")
    m6.metric("Delivery Stops",       n_stops)

    st.markdown("---")

    # ── Section 1: Selected parcels ──────────────────────────────────────────
    st.markdown("### 1️⃣ Selected Parcels (for Delivery)")
    if knapsack and knapsack["selected"]:
        df_sel = pd.DataFrame(knapsack["selected"])
        cols_to_show = [c for c in ["id","name","weight","priority","deadline","destination","value"]
                        if c in df_sel.columns]
        for fc in ["weight", "value"]:
            if fc in df_sel.columns:
                df_sel[fc] = df_sel[fc].round(2)
        if "priority" in df_sel.columns:
            df_sel["priority"] = df_sel["priority"].astype(int)
        st.dataframe(
            df_sel[cols_to_show].style.set_properties(**{"background-color": "#d4f7d4", "color": "#000"}),
            use_container_width=True, hide_index=True,
        )

        # Priority breakdown pie
        pc = df_sel["priority"].value_counts().reset_index()
        pc.columns = ["Priority", "Count"]
        fig_pie = px.pie(pc, values="Count", names="Priority",
                         title="Priority Breakdown of Selected Parcels",
                         color_discrete_sequence=px.colors.sequential.Greens)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No parcels selected by knapsack optimizer.")

    st.markdown("---")

    # ── Section 2: Optimized Route ───────────────────────────────────────────
    st.markdown("### 2️⃣ Optimized Delivery Route")
    if route and route.get("route"):
        route_list = route["route"]
        segments   = route.get("segments", [])

        st.markdown("**Delivery Sequence:**")
        for i, stop in enumerate(route_list):
            icon = "🏭" if stop == "Warehouse" else "📍"
            label = "Depart" if (i == 0) else ("Return" if (i == len(route_list) - 1) else f"Stop {i}")
            st.markdown(f"{i+1}. {icon} **{stop}** — *{label}*")

        if segments:
            seg_df = pd.DataFrame(segments, columns=["From", "To", "Distance (km)"])
            seg_df["Segment"] = seg_df["From"] + " → " + seg_df["To"]
            fig_seg = px.bar(
                seg_df, x="Segment", y="Distance (km)",
                title="Distance per Route Segment",
                color="Distance (km)", color_continuous_scale="Blues",
            )
            fig_seg.update_layout(
                xaxis_tickangle=-30,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_seg, use_container_width=True)
            st.dataframe(seg_df[["From","To","Distance (km)"]], use_container_width=True, hide_index=True)
    else:
        st.info("No route computed yet.")

    st.markdown("---")

    # ── Section 3: Total metrics recap ───────────────────────────────────────
    st.markdown("### 3️⃣ Full Metrics Recap")

    cap = float(getattr(state, "vehicle_capacity", 50.0))
    cap_util = (total_weight / cap * 100) if cap > 0 else 0

    recap = {
        "Metric": [
            "Parcels Delivered", "Parcels Rejected",
            "Total Delivery Weight", "Vehicle Capacity",
            "Capacity Utilization", "Total Delivery Value",
            "Total Route Distance", "Number of Stops",
            "2-opt Improvement",
        ],
        "Value": [
            str(n_delivered), str(n_rejected),
            f"{total_weight:.2f} kg", f"{cap:.1f} kg",
            f"{cap_util:.1f}%", str(total_value),
            f"{total_dist:.2f} km", str(n_stops),
            f"{route.get('improvement', 0):.2f} km" if route else "—",
        ],
    }
    st.dataframe(pd.DataFrame(recap), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Section 4: Export buttons ────────────────────────────────────────────
    st.markdown("### 4️⃣ Export")
    exp1, exp2 = st.columns(2)

    # Delivery plan CSV
    with exp1:
        if knapsack and knapsack["selected"]:
            df_exp = pd.DataFrame(knapsack["selected"])
            csv_bytes = df_exp.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Delivery Plan (CSV)",
                data=csv_bytes,
                file_name="delivery_plan.csv",
                mime="text/csv",
            )
        else:
            st.button("⬇️ Download Delivery Plan (CSV)", disabled=True)

    # Route JSON
    with exp2:
        if route:
            route_export = {
                "route": route.get("route", []),
                "total_distance_km": route.get("total_distance", 0),
                "segments": [
                    {"from": s[0], "to": s[1], "distance_km": s[2]}
                    for s in route.get("segments", [])
                ],
                "improvement_km": route.get("improvement", 0),
            }
            route_json = json.dumps(route_export, indent=2).encode("utf-8")
            st.download_button(
                label="⬇️ Download Route (JSON)",
                data=route_json,
                file_name="delivery_route.json",
                mime="application/json",
            )
        else:
            st.button("⬇️ Download Route (JSON)", disabled=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("🎉 All done! Your Mini-Courier delivery plan is ready.")
