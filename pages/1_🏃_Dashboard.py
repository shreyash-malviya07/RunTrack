import streamlit as st
import pandas as pd
from frontend.api_client import api
from frontend.components import require_auth, render_sidebar, render_metric_card, render_insight_card
from frontend.charts import plot_weekly_distance, plot_pace_trend

st.set_page_config(page_title="Dashboard — RunTrack", page_icon="🏃", layout="wide")
user = require_auth()
render_sidebar()

st.title("🏃 Running Dashboard")
st.caption(f"Performance analytics for **{user.get('full_name') or user.get('username')}**")

try:
    with st.spinner("Loading performance metrics..."):
        dash_data = api.get_dashboard_data()
        recent_runs = api.get_runs(limit=5)

    summary = dash_data["summary"]
    insights = dash_data["insights"]
    weekly = dash_data["weekly"]

    # 1. Top KPI Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Distance", f"{summary['total_distance_km']:.1f}", "km", "All-time mileage")
    with c2:
        render_metric_card("Total Runs", f"{summary['total_runs']}", "runs", "Completed activities")
    with c3:
        render_metric_card("Average Pace", f"{summary['average_pace_min_per_km']:.2f}", "min/km", "Weighted average")
    with c4:
        render_metric_card("Longest Run", f"{summary['longest_run_km']:.1f}", "km", "Personal record distance")

    st.markdown("---")

    # 2. Charts Row
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig_weekly = plot_weekly_distance(weekly)
        st.plotly_chart(fig_weekly, use_container_width=True)

    with col_chart2:
        all_runs = api.get_runs(limit=50)
        fig_pace = plot_pace_trend(all_runs)
        st.plotly_chart(fig_pace, use_container_width=True)

    st.markdown("---")

    # 3. Two columns: Running Insights & Recent Runs
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("💡 Coach Insights")
        if not insights:
            st.info("Log more activities to reveal personalized rule-based insights.")
        else:
            for insight in insights:
                render_insight_card(insight)

    with col_right:
        st.subheader("⏱️ Recent Runs")
        if not recent_runs:
            st.info("No runs logged yet. Head to **Add Run** to log your first activity!")
        else:
            df_recent = pd.DataFrame(recent_runs)
            df_recent["date"] = pd.to_datetime(df_recent["date"]).dt.strftime("%b %d, %Y")
            df_display = df_recent[["date", "distance_km", "duration_minutes", "pace_min_per_km"]].copy()
            df_display.columns = ["Date", "Distance (km)", "Duration (min)", "Pace (min/km)"]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Failed to load dashboard data: {str(e)}")
