from datetime import datetime, date, timedelta
from typing import Dict, Any, List
import pandas as pd
from analytics.metrics import runs_to_dataframe


def generate_weekly_report_data(df: pd.DataFrame, target_week_start: date) -> Dict[str, Any]:
    """Generate comprehensive report for a target week (Monday-Sunday) and compare with the prior week."""
    target_start_dt = pd.to_datetime(target_week_start)
    target_end_dt = target_start_dt + timedelta(days=6, hours=23, minutes=59, seconds=59)

    prior_start_dt = target_start_dt - timedelta(days=7)
    prior_end_dt = target_start_dt - timedelta(seconds=1)

    # Filter current week runs
    current_df = df[(df["date"] >= target_start_dt) & (df["date"] <= target_end_dt)] if not df.empty else pd.DataFrame()
    prior_df = df[(df["date"] >= prior_start_dt) & (df["date"] <= prior_end_dt)] if not df.empty else pd.DataFrame()

    total_runs = int(len(current_df))
    total_dist = round(float(current_df["distance_km"].sum()), 2) if not current_df.empty else 0.0
    total_dur = round(float(current_df["duration_minutes"].sum()), 2) if not current_df.empty else 0.0
    avg_pace = round(total_dur / total_dist, 2) if total_dist > 0 else 0.0
    longest_run = round(float(current_df["distance_km"].max()), 2) if not current_df.empty else 0.0

    prior_dist = round(float(prior_df["distance_km"].sum()), 2) if not prior_df.empty else 0.0
    prior_dur = round(float(prior_df["duration_minutes"].sum()), 2) if not prior_df.empty else 0.0
    prior_avg_pace = round(prior_dur / prior_dist, 2) if prior_dist > 0 else 0.0

    # Comparison metrics
    distance_change_pct = None
    if prior_dist > 0:
        distance_change_pct = round(((total_dist - prior_dist) / prior_dist) * 100.0, 1)

    pace_change = None
    if prior_avg_pace > 0 and avg_pace > 0:
        pace_change = round(avg_pace - prior_avg_pace, 2)  # negative means faster

    # Report insights
    insights = []
    if total_runs == 0:
        insights.append("No runs logged during this week.")
    else:
        if distance_change_pct is not None:
            if distance_change_pct > 0:
                insights.append(f"Mileage grew by {distance_change_pct}% compared to the prior week.")
            else:
                insights.append(f"Mileage decreased by {abs(distance_change_pct)}% compared to the prior week.")

        if pace_change is not None:
            if pace_change < 0:
                insights.append(f"Average pace improved by {abs(pace_change):.2f} min/km!")
            elif pace_change > 0:
                insights.append(f"Average pace was {pace_change:.2f} min/km more relaxed than last week.")

        if longest_run >= 15.0:
            insights.append("Impressive endurance: completed an endurance run of 15+ km.")
        elif longest_run >= 10.0:
            insights.append("Solid aerobic base: completed a double-digit 10+ km run.")

    return {
        "period": "weekly",
        "start_date": target_week_start.isoformat(),
        "end_date": (target_week_start + timedelta(days=6)).isoformat(),
        "total_runs": total_runs,
        "total_distance_km": total_dist,
        "average_pace_min_per_km": avg_pace,
        "longest_run_km": longest_run,
        "prior_distance_km": prior_dist,
        "prior_avg_pace": prior_avg_pace,
        "distance_change_pct": distance_change_pct,
        "pace_change": pace_change,
        "insights": insights,
    }


def generate_monthly_report_data(df: pd.DataFrame, year: int, month: int) -> Dict[str, Any]:
    """Generate comprehensive monthly report and compare with previous month."""
    start_dt = pd.to_datetime(f"{year:04d}-{month:02d}-01")
    # End of month
    if month == 12:
        next_month_dt = pd.to_datetime(f"{year + 1:04d}-01-01")
    else:
        next_month_dt = pd.to_datetime(f"{year:04d}-{month + 1:02d}-01")
    end_dt = next_month_dt - timedelta(seconds=1)

    # Prior month
    if month == 1:
        prior_start_dt = pd.to_datetime(f"{year - 1:04d}-12-01")
    else:
        prior_start_dt = pd.to_datetime(f"{year:04d}-{month - 1:02d}-01")
    prior_end_dt = start_dt - timedelta(seconds=1)

    current_df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)] if not df.empty else pd.DataFrame()
    prior_df = df[(df["date"] >= prior_start_dt) & (df["date"] <= prior_end_dt)] if not df.empty else pd.DataFrame()

    total_runs = int(len(current_df))
    total_dist = round(float(current_df["distance_km"].sum()), 2) if not current_df.empty else 0.0
    total_dur = round(float(current_df["duration_minutes"].sum()), 2) if not current_df.empty else 0.0
    avg_pace = round(total_dur / total_dist, 2) if total_dist > 0 else 0.0
    longest_run = round(float(current_df["distance_km"].max()), 2) if not current_df.empty else 0.0

    prior_dist = round(float(prior_df["distance_km"].sum()), 2) if not prior_df.empty else 0.0
    prior_dur = round(float(prior_df["duration_minutes"].sum()), 2) if not prior_df.empty else 0.0
    prior_avg_pace = round(prior_dur / prior_dist, 2) if prior_dist > 0 else 0.0

    distance_change_pct = None
    if prior_dist > 0:
        distance_change_pct = round(((total_dist - prior_dist) / prior_dist) * 100.0, 1)

    insights = []
    if total_runs == 0:
        insights.append("No runs logged during this month.")
    else:
        month_name = start_dt.strftime("%B %Y")
        insights.append(f"Completed {total_runs} runs totaling {total_dist} km in {month_name}.")
        if distance_change_pct is not None:
            trend_word = "increased" if distance_change_pct >= 0 else "decreased"
            insights.append(f"Monthly mileage {trend_word} by {abs(distance_change_pct)}% compared to last month.")

    return {
        "period": "monthly",
        "year": year,
        "month": month,
        "month_label": start_dt.strftime("%B %Y"),
        "total_runs": total_runs,
        "total_distance_km": total_dist,
        "average_pace_min_per_km": avg_pace,
        "longest_run_km": longest_run,
        "prior_distance_km": prior_dist,
        "prior_avg_pace": prior_avg_pace,
        "distance_change_pct": distance_change_pct,
        "insights": insights,
    }
