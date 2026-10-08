from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User, Run
from backend.dependencies import get_current_user
from backend.schemas.analytics import (
    SummaryStats,
    WeeklyAggregateItem,
    MonthlyAggregateItem,
    AnalyticsDashboardData,
    ConsistencyScore,
    RunningInsight,
)
from analytics.metrics import (
    runs_to_dataframe,
    calculate_summary,
    calculate_weekly_aggregates,
    calculate_monthly_aggregates,
    calculate_consistency_score,
)
from analytics.insights import generate_rule_based_insights

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _get_user_df(db: Session, user_id: int):
    runs = db.query(Run).filter(Run.user_id == user_id).order_by(Run.date.asc()).all()
    return runs_to_dataframe(runs)


@router.get("/summary", response_model=SummaryStats)
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all-time summary running statistics for the authenticated user."""
    df = _get_user_df(db, current_user.id)
    return calculate_summary(df)


@router.get("/weekly", response_model=List[WeeklyAggregateItem])
def get_weekly_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve weekly volume and pace aggregations for the authenticated user."""
    df = _get_user_df(db, current_user.id)
    return calculate_weekly_aggregates(df)


@router.get("/monthly", response_model=List[MonthlyAggregateItem])
def get_monthly_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve monthly volume and pace aggregations for the authenticated user."""
    df = _get_user_df(db, current_user.id)
    return calculate_monthly_aggregates(df)


@router.get("/insights", response_model=List[RunningInsight])
def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate automatic rule-based coaching insights for the authenticated user."""
    df = _get_user_df(db, current_user.id)
    return generate_rule_based_insights(df)


@router.get("/dashboard", response_model=AnalyticsDashboardData)
def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all metrics needed for the main dashboard in one optimized request."""
    df = _get_user_df(db, current_user.id)
    return {
        "summary": calculate_summary(df),
        "consistency": calculate_consistency_score(df),
        "insights": generate_rule_based_insights(df),
        "weekly": calculate_weekly_aggregates(df),
        "monthly": calculate_monthly_aggregates(df),
    }
