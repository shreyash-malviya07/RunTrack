from typing import Optional, Dict, Any
import streamlit as st


def inject_custom_styles():
    """Inject clean modern sports fitness CSS styles into the Streamlit app."""
    st.markdown("""
        <style>
        /* Modern Metric Card */
        .metric-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .metric-card:hover {
            border-color: rgba(59, 130, 246, 0.4);
            transform: translateY(-2px);
        }
        .metric-title {
            color: #94A3B8;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .metric-value {
            color: #F8FAFC;
            font-size: 1.85rem;
            font-weight: 700;
            line-height: 1.2;
        }
        .metric-unit {
            font-size: 0.9rem;
            color: #64748B;
            font-weight: 500;
            margin-left: 4px;
        }
        
        /* Insight Alert Box */
        .insight-box {
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }
        .insight-success {
            background-color: rgba(16, 185, 129, 0.1);
            border-left: 4px solid #10B981;
            color: #ECFDF5;
        }
        .insight-warning {
            background-color: rgba(245, 158, 11, 0.1);
            border-left: 4px solid #F59E0B;
            color: #FFFBEB;
        }
        .insight-info {
            background-color: rgba(59, 130, 246, 0.1);
            border-left: 4px solid #3B82F6;
            color: #EFF6FF;
        }
        
        /* Goal Progress Card */
        .goal-card {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 16px;
        }
        </style>
    """, unsafe_allow_html=True)


def require_auth() -> Dict[str, Any]:
    """Ensure the user has an active session; otherwise prompt and stop execution."""
    inject_custom_styles()
    token = st.session_state.get("token")
    user = st.session_state.get("user")

    if not token or not user:
        st.warning("🔒 You must be signed in to view this page.")
        st.info("Please navigate to the main **Home** page to sign in or register.")
        st.stop()

    return user


def render_sidebar():
    """Render common sidebar branding, runner identity, and logout option."""
    inject_custom_styles()
    user = st.session_state.get("user")
    
    with st.sidebar:
        st.markdown("### 🏃 **RunTrack**")
        st.caption("Professional Running Analytics")
        st.divider()

        if user:
            st.markdown(f"**Runner**: `{user.get('username')}`")
            if user.get("full_name"):
                st.caption(f"{user.get('full_name')}")
            st.caption(f"📧 {user.get('email')}")
            
            st.divider()
            if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
                st.session_state["token"] = None
                st.session_state["user"] = None
                st.success("Signed out successfully.")
                st.rerun()
        else:
            st.info("Not signed in.")


def render_metric_card(title: str, value: Any, unit: str = "", subtitle: Optional[str] = None):
    """Render a clean fitness metric card."""
    sub_html = f"<div style='font-size:0.75rem; color:#64748B; margin-top:4px;'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}<span class="metric-unit">{unit}</span></div>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)


def render_insight_card(insight: Dict[str, str]):
    """Render a coaching insight banner."""
    itype = insight.get("type", "info")
    title = insight.get("title", "Insight")
    msg = insight.get("message", "")

    if itype == "success":
        st.success(f"**{title}**: {msg}")
    elif itype == "warning":
        st.warning(f"**{title}**: {msg}")
    else:
        st.info(f"**{title}**: {msg}")
