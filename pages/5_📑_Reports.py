from datetime import date, timedelta
import streamlit as st
from frontend.api_client import api
from frontend.components import require_auth, render_sidebar, render_metric_card

st.set_page_config(page_title="Reports — RunTrack", page_icon="📑", layout="wide")
user = require_auth()
render_sidebar()

st.title("📑 Automated Training Reports")
st.caption("Weekly and monthly period-over-period performance summaries and coach takeaways.")

report_type = st.radio("Select Report Type", ["Weekly Report", "Monthly Report"], horizontal=True)

if report_type == "Weekly Report":
    today = date.today()
    default_monday = today - timedelta(days=today.weekday())
    selected_monday = st.date_input("Target Week (Select Monday)", value=default_monday)
    
    # Adjust to Monday if user picked other day of the week
    adjusted_monday = selected_monday - timedelta(days=selected_monday.weekday())
    if adjusted_monday != selected_monday:
        st.caption(f"Adjusted to week starting Monday: **{adjusted_monday.isoformat()}**")

    if st.button("Generate Weekly Report", type="primary"):
        try:
            with st.spinner("Generating weekly breakdown..."):
                rep = api.get_weekly_report(week_start=adjusted_monday)
            
            st.markdown(f"### 📅 Report: {rep['start_date']} to {rep['end_date']}")
            
            # Metrics comparison
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                delta_str = f"{rep['distance_change_pct']:+.1f}% vs last week" if rep['distance_change_pct'] is not None else None
                render_metric_card("Total Distance", f"{rep['total_distance_km']:.1f}", "km", delta_str)
            with c2:
                render_metric_card("Total Runs", f"{rep['total_runs']}", "runs")
            with c3:
                pace_delta = f"{rep['pace_change']:+.2f} min/km" if rep['pace_change'] is not None else None
                render_metric_card("Average Pace", f"{rep['average_pace_min_per_km']:.2f}", "min/km", pace_delta)
            with c4:
                render_metric_card("Longest Run", f"{rep['longest_run_km']:.1f}", "km")

            st.markdown("#### 💡 Weekly Coach Insights")
            if not rep["insights"]:
                st.info("No specific insights for this period.")
            else:
                for ins in rep["insights"]:
                    st.success(f"• {ins}")

        except Exception as e:
            st.error(f"Failed to generate report: {str(e)}")

else:
    # Monthly Report
    today = date.today()
    col_yr, col_mo = st.columns(2)
    with col_yr:
        selected_year = st.selectbox("Year", [today.year, today.year - 1], index=0)
    with col_mo:
        selected_month = st.selectbox(
            "Month",
            options=list(range(1, 13)),
            index=today.month - 1,
            format_func=lambda m: date(2000, m, 1).strftime("%B"),
        )

    if st.button("Generate Monthly Report", type="primary"):
        try:
            with st.spinner("Compiling monthly overview..."):
                rep = api.get_monthly_report(year=selected_year, month=selected_month)

            st.markdown(f"### 🗓️ Monthly Report: {rep['month_label']}")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                delta_str = f"{rep['distance_change_pct']:+.1f}% vs last month" if rep['distance_change_pct'] is not None else None
                render_metric_card("Monthly Distance", f"{rep['total_distance_km']:.1f}", "km", delta_str)
            with c2:
                render_metric_card("Completed Runs", f"{rep['total_runs']}", "runs")
            with c3:
                render_metric_card("Average Pace", f"{rep['average_pace_min_per_km']:.2f}", "min/km")
            with c4:
                render_metric_card("Longest Single Run", f"{rep['longest_run_km']:.1f}", "km")

            st.markdown("#### 💡 Monthly Takeaways")
            if not rep["insights"]:
                st.info("No runs recorded for this month.")
            else:
                for ins in rep["insights"]:
                    st.success(f"• {ins}")

        except Exception as e:
            st.error(f"Failed to generate monthly report: {str(e)}")
