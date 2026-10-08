from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RunBase(BaseModel):
    date: datetime = Field(..., description="Date and time of the run")
    distance_km: float = Field(..., gt=0, description="Distance in kilometers (must be > 0)")
    duration_minutes: float = Field(..., gt=0, description="Duration in minutes (must be > 0)")
    calories: Optional[int] = Field(None, ge=0, description="Calories burned (optional, >= 0)")
    avg_heart_rate: Optional[int] = Field(None, ge=40, le=220, description="Average heart rate in bpm (40-220)")
    elevation_gain: Optional[float] = Field(0.0, ge=0, description="Elevation gain in meters (>= 0)")
    notes: Optional[str] = Field(None, max_length=1000, description="Personal run notes")


class RunCreate(RunBase):
    pass


class RunUpdate(BaseModel):
    date: Optional[datetime] = None
    distance_km: Optional[float] = Field(None, gt=0)
    duration_minutes: Optional[float] = Field(None, gt=0)
    calories: Optional[int] = Field(None, ge=0)
    avg_heart_rate: Optional[int] = Field(None, ge=40, le=220)
    elevation_gain: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)


class RunResponse(RunBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    pace_min_per_km: float
    created_at: datetime
    updated_at: datetime
