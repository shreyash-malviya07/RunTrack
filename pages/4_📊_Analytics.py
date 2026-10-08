import streamlit as st
import pandas as pd
from frontend.api_client import api
from frontend.components import require_auth, render_sidebar, render_metric_card
from frontend.charts import plot_weekly_distance, plot_pace_trend, plot_distance_vs_pace, plot_monthly_volume

st.set_page_config(page_title="Analytics — RunTrack", page_icon="📊", layout="wide")
user = require_auth()
render_sidebar()

st.title("📊 Athletic Analytics & Trends")
st.caption("Deep-dive performance breakdowns, volume progression, and consistency scores.")

try:
    with st.spinner("Crunching analytics..."):
        dash_data = api.get_dashboard_data()
        runs = api.get_runs(limit=100)

    summary = dash_data["summary"]
    consistency = dash_data["consistency"]
    weekly = dash_data["weekly"]
    monthly = dash_data["monthly"]

    # 1. High-Level Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Total Distance", f"{summary['total_distance_km']:.1f}", "km", "Lifetime volume")
    with m2:
        render_metric_card("Fastest Pace", f"{summary['fastest_pace_min_per_km']:.2f}", "min/km", "All-time sprint pace")
    with m3:
        render_metric_card("Total Elevation", f"{summary['total_elevation_m']:.0f}", "m", "Vertical gain")
    with m4:
        render_metric_card("Consistency Score", f"{consistency['consistency_percentage']:.0f}", "%", f"{consistency['active_days_last_30']} active days in last 30")

    st.markdown("---")

    # 2. Volume Progression (Weekly & Monthly side-by-side)
    col1, col2 = st.columns(2)
    with col1:
        fig_w = plot_weekly_distance(weekly)
        st.plotly_chart(fig_w, use_container_width=True)
    with col2:
        fig_m = plot_monthly_volume(monthly)
        st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("---")

    # 3. Correlation & Trend Charts
    c_left, c_right = st.columns(2)
    with c_left:
        fig_p = plot_pace_trend(runs)
        st.plotly_chart(fig_p, use_container_width=True)

    with c_right:
        fig_scatter = plot_distance_vs_pace(runs)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # 4. Consistency Breakdown
    st.markdown("---")
    st.subheader("🔥 Consistency & Training Streak")
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Active Days (Last 30 Days)", f"{consistency['active_days_last_30']} days")
    with k2:
        st.metric("Consistency Target", f"{consistency['consistency_percentage']}%")
    with k3:
        st.metric("Consecutive Active Weeks", f"{consistency['current_streak_weeks']} weeks")

except Exception as e:
    st.error(f"Error loading analytics: {str(e)}")
