from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GoalBase(BaseModel):
    goal_type: str = Field(..., description="Type of goal (weekly_distance, monthly_distance, 5k, 10k, custom_distance)")
    target_value: float = Field(..., gt=0, description="Target distance in km (must be > 0)")
    start_date: date = Field(..., description="Start date of goal tracking")
    deadline: date = Field(..., description="Target deadline date")
    is_active: bool = Field(True, description="Whether goal is active")


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    goal_type: Optional[str] = None
    target_value: Optional[float] = Field(None, gt=0)
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    is_active: Optional[bool] = None


class GoalResponse(GoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    current_progress: float = 0.0
    percentage_completion: float = 0.0
    days_remaining: int = 0
    is_completed: bool = False
    created_at: datetime
