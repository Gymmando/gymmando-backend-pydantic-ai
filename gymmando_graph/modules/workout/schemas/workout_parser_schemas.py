from typing import Optional

from pydantic import BaseModel, Field


class WorkoutParserResponse(BaseModel):
    """Structured output from the Parser Agent (LLM)."""

    exercise: Optional[str] = Field(
        default=None, description="Name of the exercise (e.g., 'squats', 'bench press')"
    )
    sets: Optional[int] = Field(default=None, description="Number of sets performed")
    reps: Optional[int] = Field(
        default=None, description="Number of repetitions per set"
    )
    weight: Optional[str] = Field(
        default=None, description="Weight used (e.g., '50 lbs', 'bodyweight', '20 kg')"
    )
    rest_time: Optional[int] = Field(
        default=None, description="Rest time between sets in seconds"
    )
    comments: Optional[str] = Field(
        default=None, description="Any additional notes from the user"
    )
