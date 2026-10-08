from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# Clean athletic color palette
COLOR_PRIMARY = "#FF4B4B"      # energetic coral/red
COLOR_ACCENT = "#00D26A"       # sprint green
COLOR_SECONDARY = "#3B82F6"    # royal blue
COLOR_PURPLE = "#8B5CF6"       # purple
COLOR_BG_CARD = "#1E222D"


def plot_weekly_distance(weekly_data: List[Dict[str, Any]]) -> go.Figure:
    """Render an interactive bar chart of weekly mileage."""
    if not weekly_data:
        fig = go.Figure()
        fig.add_annotation(text="No weekly run data available yet", showarrow=False, font=dict(size=14))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    df = pd.DataFrame(weekly_data)
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["week_label"],
        y=df["distance_km"],
        name="Distance (km)",
        marker_color="#3B82F6",
        marker_line_width=0,
        opacity=0.9,
        hovertemplate="<b>%{x}</b><br>Distance: %{y:.1f} km<br>Runs: %{customdata[0]}<br>Avg Pace: %{customdata[1]:.2f} min/km<extra></extra>",
        customdata=df[["run_count", "average_pace"]].values,
    ))

    fig.update_layout(
        title="Weekly Mileage Volume (km)",
        title_font_size=16,
        xaxis_title="",
        yaxis_title="Kilometers (km)",
        template="plotly_white",
        height=340,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)"),
    )
    return fig


def plot_pace_trend(runs_data: List[Dict[str, Any]]) -> go.Figure:
    """Render an interactive line chart tracking pace evolution over time."""
    if not runs_data:
        fig = go.Figure()
        fig.add_annotation(text="No runs logged yet to display pace trend", showarrow=False, font=dict(size=14))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    df = pd.DataFrame(runs_data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Rolling average pace (window=3) if enough points
    if len(df) >= 3:
        df["rolling_pace"] = df["pace_min_per_km"].rolling(window=3, min_periods=1).mean()
    else:
        df["rolling_pace"] = df["pace_min_per_km"]

    fig = go.Figure()

    # Actual pace points
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["pace_min_per_km"],
        mode="markers",
        name="Activity Pace",
        marker=dict(size=8, color="#FF4B4B", opacity=0.7),
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Pace: %{y:.2f} min/km<br>Distance: %{customdata[0]:.1f} km<extra></extra>",
        customdata=df[["distance_km"]].values,
    ))

    # Trend line
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["rolling_pace"],
        mode="lines",
        name="Rolling Pace Trend",
        line=dict(color="#FF4B4B", width=2.5),
        hoverinfo="skip",
    ))

    fig.update_layout(
        title="Pace Progression (min/km)",
        title_font_size=16,
        xaxis_title="",
        yaxis_title="Pace (min/km)",
        template="plotly_white",
        height=340,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False),
        # In running, lower pace is faster; however displaying natural scale with gridlines is intuitive
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)"),
    )
    return fig


def plot_distance_vs_pace(runs_data: List[Dict[str, Any]]) -> go.Figure:
    """Render scatter plot comparing run distance vs. pace, colored by heart rate or calories."""
    if not runs_data:
        fig = go.Figure()
        fig.add_annotation(text="No run activities to compare", showarrow=False, font=dict(size=14))
        fig.update_layout(height=350)
        return fig

    df = pd.DataFrame(runs_data)
    df["calories"] = df["calories"].fillna(400)

    fig = px.scatter(
        df,
        x="distance_km",
        y="pace_min_per_km",
        size="duration_minutes",
        color="pace_min_per_km",
        color_continuous_scale="Viridis_r",
        hover_data=["date", "avg_heart_rate"],
        labels={"distance_km": "Distance (km)", "pace_min_per_km": "Pace (min/km)"},
        title="Distance vs. Pace Distribution",
    )

    fig.update_layout(
        template="plotly_white",
        height=360,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def plot_monthly_volume(monthly_data: List[Dict[str, Any]]) -> go.Figure:
    """Render monthly running volume bar chart."""
    if not monthly_data:
        fig = go.Figure()
        fig.add_annotation(text="No monthly history recorded yet", showarrow=False, font=dict(size=14))
        fig.update_layout(height=320)
        return fig

    df = pd.DataFrame(monthly_data)
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["month_label"],
        y=df["distance_km"],
        name="Monthly Distance",
        marker_color="#00D26A",
        hovertemplate="<b>%{x}</b><br>Total: %{y:.1f} km<br>Runs: %{customdata[0]}<extra></extra>",
        customdata=df[["run_count"]].values,
    ))

    fig.update_layout(
        title="Monthly Mileage Overview",
        title_font_size=16,
        xaxis_title="",
        yaxis_title="Total Distance (km)",
        template="plotly_white",
        height=320,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)"),
    )
    return fig
