from typing import List, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
from analytics.metrics import calculate_weekly_aggregates


def generate_rule_based_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Generate automatic, rule-based running insights and recommendations.
    Returns a list of dicts with keys: 'type' ('success', 'warning', 'info'), 'title', 'message'.
    """
    insights = []

    if df.empty or len(df) < 1:
        insights.append({
            "type": "info",
            "title": "Welcome to RunTrack!",
            "message": "Log your first run to start unlocking personalized performance analytics and coaching insights."
        })
        return insights

    # 1. Newbie encouraging milestone
    if len(df) < 3:
        insights.append({
            "type": "info",
            "title": "Building the Habit",
            "message": f"You've logged {len(df)} run(s) so far. Log at least 3 runs to unlock weekly trend analysis."
        })
        return insights

    # 2. 10% Mileage Progression Rule (Injury Prevention)
    weekly = calculate_weekly_aggregates(df)
    if len(weekly) >= 2:
        current_week = weekly[-1]
        prev_week = weekly[-2]

        if prev_week["distance_km"] > 0:
            change_pct = ((current_week["distance_km"] - prev_week["distance_km"]) / prev_week["distance_km"]) * 100

            if change_pct > 15.0:
                insights.append({
                    "type": "warning",
                    "title": "Mileage Spike Warning",
                    "message": f"Your current week volume ({current_week['distance_km']} km) is {change_pct:.1f}% higher than last week. Remember the 10% rule to prevent overuse injuries."
                })
            elif 0.0 < change_pct <= 12.0:
                insights.append({
                    "type": "success",
                    "title": "Smart Progression",
                    "message": f"Your weekly mileage increased smoothly by {change_pct:.1f}%, staying in the optimal progressive overload zone."
                })
            elif change_pct < -30.0 and current_week["distance_km"] > 0:
                insights.append({
                    "type": "info",
                    "title": "Recovery Week",
                    "message": f"Weekly mileage dropped by {abs(change_pct):.1f}%. Recovery weeks help rebuild muscle and maintain long-term stamina."
                })

    # 3. Personal Best / Milestone Detection
    all_time_longest = df["distance_km"].max()
    all_time_fastest_pace = df["pace_min_per_km"].min()
    recent_run = df.iloc[-1]

    if recent_run["distance_km"] == all_time_longest and len(df) >= 3:
        insights.append({
            "type": "success",
            "title": "New Distance Record! 🏆",
            "message": f"Your recent run of {recent_run['distance_km']:.1f} km is your longest run recorded on RunTrack!"
        })

    if recent_run["pace_min_per_km"] == all_time_fastest_pace and len(df) >= 3:
        insights.append({
            "type": "success",
            "title": "Fastest Pace Milestone! ⚡",
            "message": f"Your latest run achieved a record pace of {recent_run['pace_min_per_km']:.2f} min/km!"
        })

    # 4. Pace Progression Trend (Rolling average comparison)
    if len(df) >= 6:
        recent_avg_pace = df.tail(3)["pace_min_per_km"].mean()
        prior_avg_pace = df.iloc[-6:-3]["pace_min_per_km"].mean()
        pace_diff = prior_avg_pace - recent_avg_pace

        if pace_diff >= 0.15:  # Faster by > 9 seconds per km
            insights.append({
                "type": "success",
                "title": "Speed Improvement Detected",
                "message": f"Your rolling average pace improved by {pace_diff:.2f} min/km over your last 3 runs compared to the previous 3."
            })

    # 5. Consistency & Streak Insight
    latest_run_date = df["date"].max()
    days_since_last_run = (datetime.now() - latest_run_date.to_pydatetime().replace(tzinfo=None)).days
    if days_since_last_run >= 7:
        insights.append({
            "type": "warning",
            "title": "Time to Lace Up! 👟",
            "message": f"It has been {days_since_last_run} days since your last logged run. Consistency is key to aerobic endurance."
        })
    elif days_since_last_run <= 2:
        recent_week_runs = len(df[df["date"] >= (datetime.now() - timedelta(days=7))])
        if recent_week_runs >= 3:
            insights.append({
                "type": "success",
                "title": "Strong Training Rhythm 🔥",
                "message": f"You've logged {recent_week_runs} runs in the last 7 days. Excellent training discipline!"
            })

    return insights
