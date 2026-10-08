from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models import Goal, Run
from backend.schemas.goal import GoalCreate, GoalUpdate, GoalResponse


def enrich_goal_progress(goal: Goal, db: Session) -> Dict[str, Any]:
    """Calculate live progress and completion metrics for a goal based on user's logged runs."""
    start_dt = datetime.combine(goal.start_date, datetime.min.time())
    end_dt = datetime.combine(goal.deadline, datetime.max.time())

    runs = db.query(Run).filter(
        Run.user_id == goal.user_id,
        Run.date >= start_dt,
        Run.date <= end_dt,
    ).all()

    if goal.goal_type in ["5k", "10k"]:
        # Milestone target: maximum single run distance achieved
        max_dist = max([r.distance_km for r in runs], default=0.0)
        progress = round(max_dist, 2)
    else:
        # Cumulative volume target
        sum_dist = sum([r.distance_km for r in runs])
        progress = round(sum_dist, 2)

    target = float(goal.target_value)
    pct = round((progress / target) * 100.0, 1) if target > 0 else 0.0
    pct = min(100.0, pct)
    is_completed = progress >= target

    today = date.today()
    days_left = max(0, (goal.deadline - today).days)

    return {
        "id": goal.id,
        "user_id": goal.user_id,
        "goal_type": goal.goal_type,
        "target_value": goal.target_value,
        "start_date": goal.start_date,
        "deadline": goal.deadline,
        "is_active": goal.is_active,
        "current_progress": progress,
        "percentage_completion": pct,
        "days_remaining": days_left,
        "is_completed": is_completed,
        "created_at": goal.created_at,
    }


def create_goal(db: Session, user_id: int, goal_in: GoalCreate) -> Dict[str, Any]:
    """Create a new goal for the authenticated user."""
    db_goal = Goal(
        user_id=user_id,
        goal_type=goal_in.goal_type,
        target_value=goal_in.target_value,
        start_date=goal_in.start_date,
        deadline=goal_in.deadline,
        is_active=goal_in.is_active,
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return enrich_goal_progress(db_goal, db)


def get_user_goals(db: Session, user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieve all goals for user_id with live progress calculated."""
    query = db.query(Goal).filter(Goal.user_id == user_id)
    if active_only:
        query = query.filter(Goal.is_active == True)

    goals = query.order_by(Goal.deadline.asc()).all()
    return [enrich_goal_progress(g, db) for g in goals]


def get_goal_by_id(db: Session, user_id: int, goal_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single goal owned by user_id."""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        return None
    return enrich_goal_progress(goal, db)


def update_goal(db: Session, user_id: int, goal_id: int, goal_update: GoalUpdate) -> Optional[Dict[str, Any]]:
    """Update a goal owned by user_id."""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        return None

    update_dict = goal_update.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(goal, field, val)

    db.commit()
    db.refresh(goal)
    return enrich_goal_progress(goal, db)


def delete_goal(db: Session, user_id: int, goal_id: int) -> bool:
    """Delete a goal owned by user_id."""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        return False

    db.delete(goal)
    db.commit()
    return True
