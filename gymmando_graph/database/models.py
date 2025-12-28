"""
Database models for Supabase tables.
These models represent the database schema and are used for type-safe database operations.
"""

import uuid
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkoutDBModel(BaseModel):
    """
    Database model for the workouts table.

    This model represents a workout record as stored in Supabase.
    All fields match the database schema exactly.
    """

    id: UUID = Field(default_factory=uuid.uuid4, description="Primary key")
    user_id: str = Field(..., description="User identifier (Firebase UID)")
    exercise: str = Field(..., description="Name of the exercise")
    sets: int = Field(..., description="Number of sets performed")
    reps: int = Field(..., description="Number of repetitions per set")
    weight: str = Field(..., description="Weight used (e.g., '135 lbs', 'bodyweight')")
    rest_time: Optional[int] = Field(
        default=None, description="Rest time between sets in seconds"
    )
    comments: Optional[str] = Field(
        default=None, description="Additional notes or comments"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Timestamp when record was created"
    )

    class Config:
        """Pydantic config for the model."""

        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class WorkoutCreateModel(BaseModel):
    """
    Model for creating a new workout record.

    Excludes auto-generated fields like id and created_at.
    Used when inserting new workouts into the database.
    """

    user_id: str
    exercise: str
    sets: int
    reps: int
    weight: str
    rest_time: Optional[int] = None
    comments: Optional[str] = None

    def to_db_dict(self) -> dict[str, Any]:
        """Convert to dictionary suitable for database insertion."""
        return dict(self.model_dump(exclude_none=True))
