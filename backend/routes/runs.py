from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User
from backend.dependencies import get_current_user
from backend.schemas.run import RunCreate, RunUpdate, RunResponse
from backend.services import run_service

router = APIRouter(prefix="/runs", tags=["Runs"])


@router.post("", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
def create_run(
    run_in: RunCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log a new running activity for the authenticated user."""
    return run_service.create_run(db=db, user_id=current_user.id, run_in=run_in)


@router.get("", response_model=List[RunResponse])
def get_runs(
    start_date: Optional[datetime] = Query(None, description="Filter runs on or after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter runs on or before this date"),
    min_distance: Optional[float] = Query(None, ge=0, description="Minimum distance in km"),
    max_distance: Optional[float] = Query(None, ge=0, description="Maximum distance in km"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve running history for the authenticated user."""
    return run_service.get_user_runs(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        min_distance=min_distance,
        max_distance=max_distance,
        skip=skip,
        limit=limit,
    )


@router.get("/{run_id}", response_model=RunResponse)
def get_run(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific run owned by the authenticated user."""
    run = run_service.get_run_by_id(db=db, user_id=current_user.id, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with ID {run_id} not found."
        )
    return run


@router.put("/{run_id}", response_model=RunResponse)
def update_run(
    run_id: int,
    run_update: RunUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update details of a specific run owned by the authenticated user."""
    run = run_service.update_run(
        db=db, user_id=current_user.id, run_id=run_id, run_update=run_update
    )
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with ID {run_id} not found."
        )
    return run


@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_run(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a specific run owned by the authenticated user."""
    success = run_service.delete_run(db=db, user_id=current_user.id, run_id=run_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with ID {run_id} not found."
        )
    return None
