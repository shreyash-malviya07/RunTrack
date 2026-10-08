from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np


def runs_to_dataframe(runs: list) -> pd.DataFrame:
    """Convert SQLAlchemy Run models or run dictionaries into a typed Pandas DataFrame."""
    if not runs:
        return pd.DataFrame(columns=[
            "id", "user_id", "date", "distance_km", "duration_minutes",
            "pace_min_per_km", "calories", "avg_heart_rate", "elevation_gain"
        ])

    data = []
    for r in runs:
        if isinstance(r, dict):
            row = r.copy()
        else:
            row = {
                "id": r.id,
                "user_id": r.user_id,
                "date": r.date,
                "distance_km": float(r.distance_km),
                "duration_minutes": float(r.duration_minutes),
                "pace_min_per_km": float(r.pace_min_per_km),
                "calories": r.calories if r.calories is not None else 0,
                "avg_heart_rate": r.avg_heart_rate,
                "elevation_gain": float(r.elevation_gain or 0.0),
            }
        data.append(row)

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def calculate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate all-time high-level running KPIs."""
    if df.empty:
        return {
            "total_distance_km": 0.0,
            "total_runs": 0,
            "average_pace_min_per_km": 0.0,
            "fastest_pace_min_per_km": 0.0,
            "longest_run_km": 0.0,
            "total_duration_minutes": 0.0,
            "total_calories": 0,
            "total_elevation_m": 0.0,
        }

    total_dist = round(float(df["distance_km"].sum()), 2)
    total_runs = int(len(df))
    total_dur = round(float(df["duration_minutes"].sum()), 2)
    
    # Weighted average pace across all activities: total minutes / total km
    avg_pace = round(total_dur / total_dist, 2) if total_dist > 0 else 0.0
    fastest_pace = round(float(df["pace_min_per_km"].min()), 2)
    longest_run = round(float(df["distance_km"].max()), 2)
    total_cal = int(df["calories"].fillna(0).sum())
    total_elev = round(float(df["elevation_gain"].fillna(0).sum()), 1)

    return {
        "total_distance_km": total_dist,
        "total_runs": total_runs,
        "average_pace_min_per_km": avg_pace,
        "fastest_pace_min_per_km": fastest_pace,
        "longest_run_km": longest_run,
        "total_duration_minutes": total_dur,
        "total_calories": total_cal,
        "total_elevation_m": total_elev,
    }


def calculate_weekly_aggregates(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Group runs by calendar week and calculate volume and average pace."""
    if df.empty:
        return []

    df_copy = df.copy()
    # Group by week starting on Monday
    df_copy["week_start"] = df_copy["date"].apply(
        lambda d: d.date() - timedelta(days=d.weekday())
    )

    grouped = df_copy.groupby("week_start")
    results = []

    for week_start, group in grouped:
        dist = round(float(group["distance_km"].sum()), 2)
        dur = round(float(group["duration_minutes"].sum()), 2)
        avg_pace = round(dur / dist, 2) if dist > 0 else 0.0
        longest = round(float(group["distance_km"].max()), 2)

        results.append({
            "week_start": week_start.isoformat(),
            "week_label": f"Week of {week_start.strftime('%b %d')}",
            "distance_km": dist,
            "duration_minutes": dur,
            "run_count": int(len(group)),
            "average_pace": avg_pace,
            "longest_run_km": longest,
        })

    return sorted(results, key=lambda x: x["week_start"])


def calculate_monthly_aggregates(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Group runs by year-month and calculate volume and average pace."""
    if df.empty:
        return []

    df_copy = df.copy()
    df_copy["month_str"] = df_copy["date"].dt.strftime("%Y-%m")
    df_copy["month_label"] = df_copy["date"].dt.strftime("%B %Y")

    grouped = df_copy.groupby(["month_str", "month_label"])
    results = []

    for (month_str, month_label), group in grouped:
        dist = round(float(group["distance_km"].sum()), 2)
        dur = round(float(group["duration_minutes"].sum()), 2)
        avg_pace = round(dur / dist, 2) if dist > 0 else 0.0
        longest = round(float(group["distance_km"].max()), 2)

        results.append({
            "month_key": month_str,
            "month_label": month_label,
            "distance_km": dist,
            "duration_minutes": dur,
            "run_count": int(len(group)),
            "average_pace": avg_pace,
            "longest_run_km": longest,
        })

    return sorted(results, key=lambda x: x["month_key"])


def calculate_consistency_score(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate running consistency and streak over the past 30 days."""
    if df.empty:
        return {
            "active_days_last_30": 0,
            "consistency_percentage": 0.0,
            "current_streak_weeks": 0,
        }

    now = datetime.now()
    cutoff_30d = now - timedelta(days=30)
    
    # Filter last 30 days
    last_30_runs = df[df["date"] >= cutoff_30d]
    active_days = int(last_30_runs["date"].dt.date.nunique())
    # Assuming ideal 3-4 days/week running (14 active days / 30 = 100% athletic consistency target)
    consistency_pct = round(min(100.0, (active_days / 12.0) * 100.0), 1)

    # Calculate active weeks streak
    weekly = calculate_weekly_aggregates(df)
    streak = 0
    # Walk backwards
    for w in reversed(weekly):
        if w["run_count"] > 0:
            streak += 1
        else:
            break

    return {
        "active_days_last_30": active_days,
        "consistency_percentage": consistency_pct,
        "current_streak_weeks": streak,
    }
