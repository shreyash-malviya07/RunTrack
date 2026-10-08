from datetime import datetime, date, timedelta
import streamlit as st
import pandas as pd
from frontend.api_client import api
from frontend.components import require_auth, render_sidebar

st.set_page_config(page_title="My Runs — RunTrack", page_icon="📋", layout="wide")
user = require_auth()
render_sidebar()

st.title("📋 Running History")
st.caption("View, search, edit, and manage all your logged runs.")

# 1. Filters Section
with st.expander("🔍 Filter & Search Runs", expanded=False):
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        date_range = st.date_input(
            "Date Range",
            value=(date.today() - timedelta(days=90), date.today()),
        )
    with f_col2:
        min_dist = st.number_input("Min Distance (km)", min_value=0.0, value=0.0, step=1.0)
    with f_col3:
        max_dist = st.number_input("Max Distance (km)", min_value=0.0, value=100.0, step=1.0)

# Fetch runs
try:
    start_dt = None
    end_dt = None
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_dt = datetime.combine(date_range[0], datetime.min.time())
        end_dt = datetime.combine(date_range[1], datetime.max.time())

    runs = api.get_runs(
        start_date=start_dt,
        end_date=end_dt,
        min_distance=min_dist if min_dist > 0 else None,
        max_distance=max_dist if max_dist < 100 else None,
        limit=200,
    )

    if not runs:
        st.info("No runs found matching the filter criteria. Log a run via **Add Run**!")
    else:
        st.write(f"Showing **{len(runs)}** activities")

        # Table Display
        table_rows = []
        for r in runs:
            dt = pd.to_datetime(r["date"]).strftime("%Y-%m-%d %H:%M")
            table_rows.append({
                "ID": r["id"],
                "Date": dt,
                "Distance (km)": f"{r['distance_km']:.2f}",
                "Duration (min)": f"{r['duration_minutes']:.1f}",
                "Pace (min/km)": f"{r['pace_min_per_km']:.2f}",
                "Calories": r.get("calories") or "-",
                "Avg HR (bpm)": r.get("avg_heart_rate") or "-",
                "Elevation (m)": f"{r.get('elevation_gain', 0):.0f}",
                "Notes": r.get("notes") or "",
            })
        
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🛠️ Manage Activities")

        # Action Selector
        run_options = {f"Run #{r['id']} — {r['distance_km']}km on {r['date'][:10]}": r['id'] for r in runs}
        selected_label = st.selectbox("Select a run to modify or delete:", list(run_options.keys()))
        selected_run_id = run_options[selected_label]

        # Fetch selected run details
        current_run = next((r for r in runs if r["id"] == selected_run_id), None)

        if current_run:
            tab_edit, tab_delete = st.tabs(["✏️ Edit Run", "🗑️ Delete Run"])

            with tab_edit:
                with st.form(f"edit_form_{selected_run_id}"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        new_dist = st.number_input(
                            "Distance (km)",
                            min_value=0.1,
                            value=float(current_run["distance_km"]),
                            step=0.1,
                        )
                        new_dur = st.number_input(
                            "Duration (min)",
                            min_value=0.1,
                            value=float(current_run["duration_minutes"]),
                            step=0.5,
                        )
                        new_notes = st.text_area("Notes", value=current_run.get("notes") or "")

                    with ec2:
                        new_cal = st.number_input(
                            "Calories (kcal)",
                            min_value=0,
                            value=int(current_run.get("calories") or 0),
                            step=10,
                        )
                        new_hr = st.number_input(
                            "Avg Heart Rate (bpm)",
                            min_value=40,
                            max_value=220,
                            value=int(current_run.get("avg_heart_rate") or 140),
                        )
                        new_elev = st.number_input(
                            "Elevation Gain (m)",
                            min_value=0.0,
                            value=float(current_run.get("elevation_gain") or 0.0),
                            step=5.0,
                        )

                    preview_pace = new_dur / new_dist if new_dist > 0 else 0
                    st.caption(f"Estimated Pace: **{preview_pace:.2f} min/km**")
                    update_submitted = st.form_submit_button("Save Changes", type="primary")

                    if update_submitted:
                        try:
                            api.update_run(selected_run_id, {
                                "distance_km": new_dist,
                                "duration_minutes": new_dur,
                                "calories": new_cal if new_cal > 0 else None,
                                "avg_heart_rate": new_hr if new_hr > 40 else None,
                                "elevation_gain": new_elev,
                                "notes": new_notes if new_notes else None,
                            })
                            st.success("Run updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update run: {str(e)}")

            with tab_delete:
                st.warning(f"Are you sure you want to delete **Run #{selected_run_id}** ({current_run['distance_km']} km)? This action cannot be undone.")
                if st.button("Confirm Delete", type="primary", key=f"del_btn_{selected_run_id}"):
                    try:
                        api.delete_run(selected_run_id)
                        st.success("Run deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete run: {str(e)}")

except Exception as e:
    st.error(f"Error loading runs: {str(e)}")
