import streamlit as st
from frontend.api_client import api
from frontend.components import inject_custom_styles, render_sidebar, render_metric_card

st.set_page_config(
    page_title="RunTrack — Professional Running Analytics",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None

inject_custom_styles()
render_sidebar()

# Authentication Check
if not st.session_state["token"]:
    st.markdown("<h1 style='text-align: center;'>🏃 RunTrack</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #94A3B8; font-size: 1.15rem; margin-bottom: 2rem;'>"
        "Professional Athletic Analytics & Performance Intelligence Platform"
        "</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create Account"])

        with tab_login:
            st.markdown("#### Access Your Running Profile")
            with st.form("login_form"):
                login_identifier = st.text_input("Username or Email", placeholder="e.g. runner1 or user@example.com")
                login_password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                if submitted:
                    if not login_identifier or not login_password:
                        st.error("Please provide both username/email and password.")
                    else:
                        with st.spinner("Authenticating..."):
                            try:
                                auth_data = api.login(login_identifier.strip(), login_password)
                                st.session_state["token"] = auth_data["access_token"]
                                st.session_state["user"] = auth_data["user"]
                                st.success("Signed in successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

        with tab_register:
            st.markdown("#### New Runner Registration")
            with st.form("register_form"):
                reg_name = st.text_input("Full Name (optional)", placeholder="e.g. Alex Morgan")
                reg_username = st.text_input("Username", placeholder="e.g. alex_runs")
                reg_email = st.text_input("Email Address", placeholder="e.g. alex@example.com")
                reg_password = st.text_input("Password (min 6 characters)", type="password", placeholder="••••••••")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                reg_submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                if reg_submit:
                    if not reg_username or not reg_email or not reg_password:
                        st.error("Please fill in all required fields.")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    else:
                        with st.spinner("Creating your account..."):
                            try:
                                reg_data = api.register(
                                    email=reg_email.strip(),
                                    username=reg_username.strip(),
                                    password=reg_password,
                                    full_name=reg_name.strip() if reg_name else None,
                                )
                                st.session_state["token"] = reg_data["access_token"]
                                st.session_state["user"] = reg_data["user"]
                                st.success("Account created successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

else:
    # Authenticated Landing View
    user = st.session_state["user"]
    display_name = user.get("full_name") or user.get("username")
    
    st.markdown(f"## 🏃 Welcome back, **{display_name}**!")
    st.caption("Here is your real-time training snapshot. Use the sidebar to explore deep analytics, reports, and goals.")

    try:
        summary = api.get_summary()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Total Distance", f"{summary['total_distance_km']:.1f}", "km")
        with col2:
            render_metric_card("Total Runs", f"{summary['total_runs']}", "activities")
        with col3:
            render_metric_card("Average Pace", f"{summary['average_pace_min_per_km']:.2f}", "min/km")
        with col4:
            render_metric_card("Longest Run", f"{summary['longest_run_km']:.1f}", "km")
    except Exception as e:
        st.info("Log your first run to generate lifetime statistics!")

    st.markdown("---")
    st.markdown("### ⚡ Quick Navigation")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info("📊 **Dashboard**\n\nHigh-level weekly volume, pace progression, and smart coach insights.")
    with c2:
        st.info("➕ **Add Run**\n\nLog new running activities with instantaneous pace calculation.")
    with c3:
        st.info("📋 **My Runs**\n\nSearch, filter, view, edit, or delete logged running history.")
    with c4:
        st.info("🎯 **Goals**\n\nSet targets (5K, 10K, weekly mileage) and track progress toward deadlines.")
