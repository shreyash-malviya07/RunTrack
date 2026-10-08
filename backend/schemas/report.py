from typing import List, Optional
from pydantic import BaseModel


class WeeklyReportResponse(BaseModel):
    period: str = "weekly"
    start_date: str
    end_date: str
    total_runs: int
    total_distance_km: float
    average_pace_min_per_km: float
    longest_run_km: float
    prior_distance_km: float
    prior_avg_pace: float
    distance_change_pct: Optional[float] = None
    pace_change: Optional[float] = None
    insights: List[str]


class MonthlyReportResponse(BaseModel):
    period: str = "monthly"
    year: int
    month: int
    month_label: str
    total_runs: int
    total_distance_km: float
    average_pace_min_per_km: float
    longest_run_km: float
    prior_distance_km: float
    prior_avg_pace: float
    distance_change_pct: Optional[float] = None
    insights: List[str]
