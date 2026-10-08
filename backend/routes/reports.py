from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User, Run
from backend.dependencies import get_current_user
from backend.schemas.report import WeeklyReportResponse, MonthlyReportResponse
from analytics.metrics import runs_to_dataframe
from analytics.reports import generate_weekly_report_data, generate_monthly_report_data

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/weekly", response_model=WeeklyReportResponse)
def get_weekly_report(
    week_start: Optional[date] = Query(None, description="Starting Monday of target week (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate or retrieve weekly performance report comparing with previous week."""
    if not week_start:
        today = date.today()
        # Find current week Monday
        week_start = today - timedelta(days=today.weekday())

    runs = db.query(Run).filter(Run.user_id == current_user.id).order_by(Run.date.asc()).all()
    df = runs_to_dataframe(runs)
    return generate_weekly_report_data(df, week_start)


@router.get("/monthly", response_model=MonthlyReportResponse)
def get_monthly_report(
    year: Optional[int] = Query(None, description="Target year (e.g. 2026)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Target month (1-12)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate or retrieve monthly performance report comparing with previous month."""
    today = date.today()
    target_year = year or today.year
    target_month = month or today.month

    runs = db.query(Run).filter(Run.user_id == current_user.id).order_by(Run.date.asc()).all()
    df = runs_to_dataframe(runs)
    return generate_monthly_report_data(df, target_year, target_month)
