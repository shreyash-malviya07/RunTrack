from typing import List, Optional
from pydantic import BaseModel


class SummaryStats(BaseModel):
    total_distance_km: float
    total_runs: int
    average_pace_min_per_km: float
    fastest_pace_min_per_km: float
    longest_run_km: float
    total_duration_minutes: float
    total_calories: int
    total_elevation_m: float


class WeeklyAggregateItem(BaseModel):
    week_start: str
    week_label: str
    distance_km: float
    duration_minutes: float
    run_count: int
    average_pace: float
    longest_run_km: float


class MonthlyAggregateItem(BaseModel):
    month_key: str
    month_label: str
    distance_km: float
    duration_minutes: float
    run_count: int
    average_pace: float
    longest_run_km: float


class ConsistencyScore(BaseModel):
    active_days_last_30: int
    consistency_percentage: float
    current_streak_weeks: int


class RunningInsight(BaseModel):
    type: str  # success, warning, info
    title: str
    message: str


class AnalyticsDashboardData(BaseModel):
    summary: SummaryStats
    consistency: ConsistencyScore
    insights: List[RunningInsight]
    weekly: List[WeeklyAggregateItem]
    monthly: List[MonthlyAggregateItem]
