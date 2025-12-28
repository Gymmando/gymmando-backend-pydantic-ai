from typing import List, Optional

from pydantic import BaseModel, Field


class WorkoutState(BaseModel):
    """State that flows through all nodes."""

    # User input
    user_input: str
    user_id: str

    # Intent classification
    intent: Optional[str] = None  # "put" or "get"

    # Workout data (extracted by parser)
    exercise: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[str] = None
    rest_time: Optional[int] = None
    comments: Optional[str] = None

    # Validation results
    validation_status: Optional[str] = None  # "complete" or "incomplete"
    missing_fields: List[str] = Field(default_factory=list)

    # Response
    response: str = ""


## How Data Moves:

### Between Nodes (Same Agent/Graph):
# **State object gets passed and updated:**
# ```
# Parser Node receives: WorkoutState(user_input="3 sets of squats")
# Parser Node updates: state.sets = 3, state.exercise = "squats"
# Parser Node returns: WorkoutState(sets=3, exercise="squats", reps=None, ...)
#     ↓
# Validator Node receives: same WorkoutState object
# Validator Node updates: state.missing_fields = ["reps", "weight"]
# Validator Node returns: updated WorkoutState
