import streamlit as st
import pandas as pd
from frontend.api_client import api
from frontend.components import require_auth, render_sidebar, render_metric_card

st.set_page_config(page_title="Profile — RunTrack", page_icon="👤", layout="wide")
user = require_auth()
render_sidebar()

st.title("👤 Runner Profile")

try:
    me = api.get_me()
    summary = api.get_summary()

    col_info, col_stats = st.columns([1, 1])

    with col_info:
        st.subheader("Account Details")
        st.write(f"**Username**: `{me.get('username')}`")
        st.write(f"**Full Name**: {me.get('full_name') or 'Not set'}")
        st.write(f"**Email Address**: `{me.get('email')}`")
        joined_date = pd.to_datetime(me.get('created_at')).strftime("%B %d, %Y") if me.get('created_at') else "Recent"
        st.write(f"**Member Since**: {joined_date}")

        st.markdown("---")
        if st.button("🚪 Sign Out of RunTrack", type="primary"):
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.success("Successfully logged out.")
            st.rerun()

    with col_stats:
        st.subheader("🏆 Lifetime Running Milestones")
        c1, c2 = st.columns(2)
        with c1:
            render_metric_card("Total Distance", f"{summary['total_distance_km']:.1f}", "km")
            render_metric_card("Total Calories", f"{summary['total_calories']:,}", "kcal")
        with c2:
            render_metric_card("Activities Logged", f"{summary['total_runs']}", "runs")
            render_metric_card("Longest Run", f"{summary['longest_run_km']:.1f}", "km")

except Exception as e:
    st.error(f"Error fetching profile data: {str(e)}")
