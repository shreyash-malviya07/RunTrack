from datetime import datetime, date, time
import streamlit as st
from frontend.api_client import api
from frontend.components import require_auth, render_sidebar

st.set_page_config(page_title="Add Run — RunTrack", page_icon="➕", layout="wide")
user = require_auth()
render_sidebar()

st.title("➕ Log a Running Activity")
st.caption("Record your training metrics to update your lifetime analytics and progress.")

col_main, col_preview = st.columns([2, 1])

with col_main:
    with st.form("add_run_form"):
        c1, c2 = st.columns(2)
        with c1:
            run_date = st.date_input("Run Date", value=date.today())
            run_distance = st.number_input("Distance (km)", min_value=0.1, max_value=250.0, value=5.0, step=0.1)
            run_calories = st.number_input("Calories (kcal, optional)", min_value=0, max_value=10000, value=350, step=25)
            run_elevation = st.number_input("Elevation Gain (m, optional)", min_value=0.0, max_value=8000.0, value=25.0, step=5.0)

        with c2:
            run_time = st.time_input("Start Time", value=datetime.now().time())
            run_duration = st.number_input("Duration (minutes)", min_value=1.0, max_value=1440.0, value=27.5, step=0.5)
            run_hr = st.number_input("Average Heart Rate (bpm, optional)", min_value=0, max_value=220, value=152, step=1)
            run_notes = st.text_input("Notes / Route (optional)", placeholder="e.g. Sunny morning jog along the river path")

        # Instant pace calculation preview
        calculated_pace = run_duration / run_distance if run_distance > 0 else 0
        pace_mins = int(calculated_pace)
        pace_secs = int((calculated_pace - pace_mins) * 60)
        
        st.markdown(f"**⚡ Estimated Pace**: `{pace_mins}:{pace_secs:02d} min/km` (`{calculated_pace:.2f}` decimal)")
        
        submitted = st.form_submit_button("Save Activity", type="primary", use_container_width=True)

        if submitted:
            run_datetime = datetime.combine(run_date, run_time)
            payload = {
                "date": run_datetime.isoformat(),
                "distance_km": run_distance,
                "duration_minutes": run_duration,
                "calories": int(run_calories) if run_calories > 0 else None,
                "avg_heart_rate": int(run_hr) if run_hr >= 40 else None,
                "elevation_gain": run_elevation,
                "notes": run_notes.strip() if run_notes else None,
            }

            try:
                with st.spinner("Saving run..."):
                    created = api.create_run(payload)
                st.success(f"🎉 Run logged successfully! Recorded {created['distance_km']} km at {created['pace_min_per_km']:.2f} min/km.")
                st.balloons()
            except Exception as e:
                st.error(f"Error saving run: {str(e)}")

with col_preview:
    st.markdown("### 💡 Running Tips")
    st.info(
        "**Pace Breakdown**:\n\n"
        "- **Easy / Recovery**: 6:00 - 7:30 min/km\n"
        "- **Tempo / Threshold**: 4:45 - 5:45 min/km\n"
        "- **Interval / Speed**: < 4:30 min/km\n\n"
        "Accurate heart rate data unlocks aerobic zone efficiency metrics in the Analytics tab!"
    )
