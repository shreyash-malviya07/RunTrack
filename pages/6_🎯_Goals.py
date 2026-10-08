from datetime import date, timedelta
import streamlit as st
from frontend.api_client import api
from frontend.components import require_auth, render_sidebar

st.set_page_config(page_title="Goals — RunTrack", page_icon="🎯", layout="wide")
user = require_auth()
render_sidebar()

st.title("🎯 Running Targets & Goals")
st.caption("Stay motivated by setting distance milestones and tracking real-time progress.")

tab_active, tab_new = st.tabs(["🏆 Active & Past Goals", "➕ Create New Goal"])

with tab_new:
    st.subheader("Set a New Running Target")
    with st.form("create_goal_form"):
        col_type, col_target = st.columns(2)
        with col_type:
            goal_type = st.selectbox(
                "Goal Type",
                [
                    ("weekly_distance", "Weekly Mileage Volume"),
                    ("monthly_distance", "Monthly Mileage Volume"),
                    ("5k", "5K Single Run Milestone"),
                    ("10k", "10K Single Run Milestone"),
                    ("custom_distance", "Custom Cumulative Distance"),
                ],
                format_func=lambda x: x[1],
            )[0]
        
        with col_target:
            default_val = 5.0 if goal_type == "5k" else (10.0 if goal_type == "10k" else 25.0)
            target_value = st.number_input("Target Distance (km)", min_value=1.0, max_value=5000.0, value=default_val, step=1.0)

        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input("Start Date", value=date.today())
        with col_end:
            deadline = st.date_input("Deadline", value=date.today() + timedelta(days=30))

        submit_goal = st.form_submit_button("Create Target", type="primary", use_container_width=True)

        if submit_goal:
            if deadline < start_date:
                st.error("Deadline cannot be earlier than start date.")
            else:
                try:
                    payload = {
                        "goal_type": goal_type,
                        "target_value": target_value,
                        "start_date": start_date.isoformat(),
                        "deadline": deadline.isoformat(),
                        "is_active": True,
                    }
                    api.create_goal(payload)
                    st.success("Target created! Check your progress in the Active Goals tab.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create goal: {str(e)}")

with tab_active:
    try:
        goals = api.get_goals()
        if not goals:
            st.info("No active goals found. Use the 'Create New Goal' tab above to set your first target!")
        else:
            for g in goals:
                with st.container():
                    pct = g["percentage_completion"]
                    prog = g["current_progress"]
                    target = g["target_value"]
                    is_done = g["is_completed"]

                    st.markdown(f"#### 🎯 {g['goal_type'].replace('_', ' ').title()}: **{target:.1f} km**")
                    
                    # Progress Bar
                    bar_val = min(1.0, max(0.0, pct / 100.0))
                    st.progress(bar_val)

                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        status_badge = "✅ COMPLETED" if is_done else f"{pct:.1f}% COMPLETE"
                        st.write(f"**Status**: `{status_badge}`")
                    with c2:
                        st.write(f"**Progress**: `{prog:.1f} / {target:.1f} km`")
                    with c3:
                        st.write(f"**Deadline**: `{g['deadline']}` ({g['days_remaining']} days left)")
                    with c4:
                        if st.button("Delete Goal", key=f"del_goal_{g['id']}", type="secondary"):
                            api.delete_goal(g["id"])
                            st.success("Goal removed.")
                            st.rerun()
                    
                    st.divider()

    except Exception as e:
        st.error(f"Error loading goals: {str(e)}")
