from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import Run
from backend.schemas.run import RunCreate, RunUpdate


def calculate_pace(duration_minutes: float, distance_km: float) -> float:
    """Calculate running pace in minutes per kilometer."""
    if distance_km <= 0:
        return 0.0
    return round(duration_minutes / distance_km, 2)


def create_run(db: Session, user_id: int, run_in: RunCreate) -> Run:
    """Create a new running activity for the user."""
    pace = calculate_pace(run_in.duration_minutes, run_in.distance_km)
    db_run = Run(
        user_id=user_id,
        date=run_in.date,
        distance_km=run_in.distance_km,
        duration_minutes=run_in.duration_minutes,
        pace_min_per_km=pace,
        calories=run_in.calories,
        avg_heart_rate=run_in.avg_heart_rate,
        elevation_gain=run_in.elevation_gain or 0.0,
        notes=run_in.notes,
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run


def get_user_runs(
    db: Session,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Run]:
    """Retrieve runs belonging exclusively to user_id with optional filters."""
    query = db.query(Run).filter(Run.user_id == user_id)

    if start_date:
        query = query.filter(Run.date >= start_date)
    if end_date:
        query = query.filter(Run.date <= end_date)
    if min_distance is not None:
        query = query.filter(Run.distance_km >= min_distance)
    if max_distance is not None:
        query = query.filter(Run.distance_km <= max_distance)

    return query.order_by(Run.date.desc()).offset(skip).limit(limit).all()


def get_run_by_id(db: Session, user_id: int, run_id: int) -> Optional[Run]:
    """Retrieve a single run, enforcing user ownership."""
    return db.query(Run).filter(Run.id == run_id, Run.user_id == user_id).first()


def update_run(db: Session, user_id: int, run_id: int, run_update: RunUpdate) -> Optional[Run]:
    """Update a run if owned by user_id, recalculating pace if needed."""
    db_run = get_run_by_id(db, user_id, run_id)
    if not db_run:
        return None

    update_dict = run_update.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(db_run, field, value)

    # Recalculate pace if either distance or duration changed
    db_run.pace_min_per_km = calculate_pace(db_run.duration_minutes, db_run.distance_km)

    db.commit()
    db.refresh(db_run)
    return db_run


def delete_run(db: Session, user_id: int, run_id: int) -> bool:
    """Delete a run if owned by user_id."""
    db_run = get_run_by_id(db, user_id, run_id)
    if not db_run:
        return False

    db.delete(db_run)
    db.commit()
    return True
