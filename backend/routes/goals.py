from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User
from backend.dependencies import get_current_user
from backend.schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from backend.services import goal_service

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_in: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new running goal for the authenticated user."""
    return goal_service.create_goal(db=db, user_id=current_user.id, goal_in=goal_in)


@router.get("", response_model=List[GoalResponse])
def get_goals(
    active_only: bool = Query(False, description="Filter only active goals"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all goals with real-time calculated progress for the authenticated user."""
    return goal_service.get_user_goals(db=db, user_id=current_user.id, active_only=active_only)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details and progress for a specific goal."""
    goal = goal_service.get_goal_by_id(db=db, user_id=current_user.id, goal_id=goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found."
        )
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a specific goal."""
    goal = goal_service.update_goal(
        db=db, user_id=current_user.id, goal_id=goal_id, goal_update=goal_update
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found."
        )
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a goal owned by the authenticated user."""
    success = goal_service.delete_goal(db=db, user_id=current_user.id, goal_id=goal_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found."
        )
    return None
