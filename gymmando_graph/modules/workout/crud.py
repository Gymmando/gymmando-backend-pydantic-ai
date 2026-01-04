"""
Workout CRUD operations.
Handles all database operations for workouts.
"""

from typing import List, Optional
from uuid import UUID

from gymmando_graph.database import get_supabase_client
from gymmando_graph.database.models import WorkoutCreateModel, WorkoutDBModel
from gymmando_graph.modules.workout.schemas import WorkoutState
from gymmando_graph.utils import Logger

logger = Logger().get_logger()


class WorkoutCRUD:
    """CRUD operations for workout table."""

    def __init__(self):
        """Initialize the workout CRUD service."""
        self.table_name = "workouts"

    def _get_client(self):
        """Get Supabase client (lazy loading)."""
        return get_supabase_client()

    def create(self, state: WorkoutState) -> Optional[WorkoutDBModel]:
        """
        Create a new workout record.

        Args:
            state: WorkoutState containing workout data

        Returns:
            WorkoutDBModel if successful, None otherwise
        """
        # Validate that required fields are present
        if not state.exercise or not state.sets or not state.reps or not state.weight:
            error_msg = "Cannot create workout: missing required fields"
            logger.error(error_msg)
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
            logger.info(
                f"💾 Creating workout: {workout_create.exercise} - "
                f"{workout_create.sets}x{workout_create.reps} @ {workout_create.weight} "
                f"for user_id: {workout_create.user_id}"
            )

            client = self._get_client()
            response = (
                client.table(self.table_name)
                .insert(workout_create.to_db_dict())
                .execute()
            )

            if response.data and len(response.data) > 0:
                saved_workout = WorkoutDBModel(**response.data[0])
                logger.info(f"Workout created successfully with ID: {saved_workout.id}")
                return saved_workout
            else:
                logger.error("Database insert returned no data")
                return None

        except Exception as e:
            logger.error(f"Failed to create workout: {e}", exc_info=True)
            raise

    def read(
        self,
        user_id: str,
        exercise: Optional[str] = None,
        exercise_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = 10,
        order_by: Optional[str] = "created_at",
        order_direction: Optional[str] = "desc",
    ) -> List[WorkoutDBModel]:
        """
        Read workouts from the database based on filters.

        Args:
            user_id: The user ID to filter workouts by (required)
            exercise: Filter by specific exercise name (e.g., "squats", "bench press")
            exercise_type: Filter by exercise type/category (e.g., "legs", "chest", "arms")
            start_date: Start date for date range filter (YYYY-MM-DD format)
            end_date: End date for date range filter (YYYY-MM-DD format)
            limit: Maximum number of workouts to return (default: 10)
            order_by: Field to order by (default: "created_at")
            order_direction: Order direction - "asc" or "desc" (default: "desc")

        Returns:
            List of WorkoutDBModel instances
        """
        try:
            logger.info(
                f"🔍 Reading workouts with params: user_id={user_id}, "
                f"exercise={exercise}, limit={limit}"
            )

            client = self._get_client()
            query = client.table(self.table_name).select("*").eq("user_id", user_id)

            # Apply filters
            if exercise:
                query = query.ilike("exercise", f"%{exercise}%")
                logger.info(f"Applied exercise filter: {exercise}")

            # TODO: Add exercise_type filtering when we have that field in the schema

            if start_date:
                query = query.gte("created_at", start_date)

            if end_date:
                query = query.lte("created_at", end_date)

            # Apply ordering
            desc_order = (order_direction or "desc").lower() == "desc"
            query = query.order(order_by or "created_at", desc=desc_order)

            # Apply limit
            if limit:
                query = query.limit(limit)

            # Execute query
            response = query.execute()
            logger.info(
                f"Query returned {len(response.data) if response.data else 0} workouts"
            )

            if response.data:
                return [WorkoutDBModel(**item) for item in response.data]

            return []

        except Exception as e:
            logger.error(f"Failed to read workouts: {e}", exc_info=True)
            return []

    def update(
        self, workout_id: UUID, user_id: str, data: dict
    ) -> Optional[WorkoutDBModel]:
        """
        Update an existing workout record.

        Args:
            workout_id: UUID of the workout to update
            user_id: User ID for security filtering
            data: Dictionary containing the fields to update
                  (e.g., {"sets": 5, "reps": 10, "weight": "225 lbs"})

        Returns:
            Updated WorkoutDBModel if successful, None otherwise
        """
        try:
            logger.info(
                f"✏️ Updating workout {workout_id} for user {user_id} with data: {data}"
            )

            client = self._get_client()
            response = (
                client.table(self.table_name)
                .update(data)
                .eq("id", str(workout_id))
                .eq("user_id", user_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                updated_workout = WorkoutDBModel(**response.data[0])
                logger.info(f"Workout {workout_id} updated successfully")
                return updated_workout
            else:
                logger.warning(
                    f"No workout found with ID {workout_id} for user {user_id}"
                )
                return None

        except Exception as e:
            logger.error(f"Failed to update workout {workout_id}: {e}", exc_info=True)
            return None

    def delete(self, workout_id: UUID, user_id: str) -> bool:
        """
        Delete a workout record.

        Args:
            workout_id: UUID of the workout to delete
            user_id: User ID for security filtering

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            logger.info(f"🗑️ Deleting workout {workout_id} for user {user_id}")

            client = self._get_client()
            response = (
                client.table(self.table_name)
                .delete()
                .eq("id", str(workout_id))
                .eq("user_id", user_id)
                .execute()
            )

            success = bool(response.data)
            if success:
                logger.info(f"Workout {workout_id} deleted successfully")
            else:
                logger.warning(
                    f"No workout found with ID {workout_id} for user {user_id}"
                )

            return success

        except Exception as e:
            logger.error(f"Failed to delete workout {workout_id}: {e}", exc_info=True)
            return False
