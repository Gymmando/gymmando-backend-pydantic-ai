"""
Database operations for workout module.
Handles saving and retrieving workout data from Supabase.
"""

from typing import Optional
from uuid import UUID

# Import the function instead of the global variable
from gymmando_graph.database import get_supabase_client
from gymmando_graph.database.models import WorkoutCreateModel, WorkoutDBModel
from gymmando_graph.modules.workout.schemas import WorkoutState
from gymmando_graph.utils import Logger

# Note: Ideally, Logger should also be initialized lazily,
# but let's fix the Database first as it's the primary network bottleneck.
logger = Logger().get_logger()


class WorkoutDatabase:
    """
    Database service for workout operations.

    Provides methods to save, retrieve, and query workout data from Supabase.
    """

    def __init__(self):
        """Initialize the workout database service."""
        self.table_name = "workouts"
        self.logger = logger

    def save_workout(self, state: WorkoutState) -> Optional[WorkoutDBModel]:
        """
        Save a validated workout to the database.
        """
        # Validate that required fields are present
        if not state.exercise or not state.sets or not state.reps or not state.weight:
            error_msg = "Cannot save workout: missing required fields"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Create database model from state
        workout_create = WorkoutCreateModel(
            user_id=state.user_id,
            exercise=state.exercise,
            sets=state.sets,
            reps=state.reps,
            weight=state.weight,
            rest_time=state.rest_time,
            comments=state.comments,
        )

        try:
            # Insert into database
            self.logger.info(
                f"Saving workout: {workout_create.exercise} - "
                f"{workout_create.sets}x{workout_create.reps} @ {workout_create.weight} "
                f"for user {workout_create.user_id}"
            )

            # FIX: Get the client right before use
            client = get_supabase_client()
            response = (
                client.table(self.table_name)
                .insert(workout_create.to_db_dict())
                .execute()
            )

            if response.data and len(response.data) > 0:
                saved_workout = WorkoutDBModel(**response.data[0])
                self.logger.info(
                    f"Workout saved successfully with ID: {saved_workout.id}"
                )
                return saved_workout
            else:
                self.logger.error("Database insert returned no data")
                return None

        except Exception as e:
            self.logger.error(f"Failed to save workout to database: {e}", exc_info=True)
            raise

    def get_workout_by_id(
        self, workout_id: UUID, user_id: str
    ) -> Optional[WorkoutDBModel]:
        """
        Retrieve a workout by ID for a specific user.
        """
        try:
            # FIX: Get the client here
            client = get_supabase_client()
            response = (
                client.table(self.table_name)
                .select("*")
                .eq("id", str(workout_id))
                .eq("user_id", user_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return WorkoutDBModel(**response.data[0])
            return None

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve workout {workout_id}: {e}", exc_info=True
            )
            return None

    def get_user_workouts(
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> list[WorkoutDBModel]:
        """
        Retrieve workouts for a specific user.
        """
        try:
            # FIX: Get the client here
            client = get_supabase_client()
            response = (
                client.table(self.table_name)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )

            workouts = [WorkoutDBModel(**item) for item in response.data]
            self.logger.info(f"Retrieved {len(workouts)} workouts for user {user_id}")
            return workouts

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve workouts for user {user_id}: {e}", exc_info=True
            )
            return []
