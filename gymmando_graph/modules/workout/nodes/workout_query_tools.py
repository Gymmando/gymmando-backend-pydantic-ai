"""
Query tools for retrieving workout data from the database.
"""

import json
from typing import Optional

from dotenv import load_dotenv
from langchain_core.tools import StructuredTool

from gymmando_graph.database import get_supabase_client
from gymmando_graph.database.models import WorkoutDBModel
from gymmando_graph.utils import Logger

load_dotenv()

logger = Logger().get_logger()


def _query_workouts_impl(
    user_id: str,
    exercise: Optional[str] = None,
    exercise_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 10,
    order_by: Optional[str] = "created_at",
    order_direction: Optional[str] = "desc",
) -> str:
    """
    Query workouts from the database based on various filters.

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
        JSON string of workout data matching the query
    """
    try:
        logger.info(
            f"Querying workouts with params: user_id={user_id}, exercise={exercise}, limit={limit}"
        )
        client = get_supabase_client()
        query = client.table("workouts").select("*").eq("user_id", user_id)

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
            workouts = [WorkoutDBModel(**item) for item in response.data]
            # Convert to JSON string for LLM consumption
            workouts_dict = [workout.model_dump() for workout in workouts]
            return json.dumps(workouts_dict, default=str)

        return json.dumps([])

    except Exception as e:
        logger.error(f"Failed to query workouts: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


# Create the LangChain tool
query_workouts = StructuredTool.from_function(
    func=_query_workouts_impl,
    name="query_workouts",
    description="Query workouts from the database based on various filters. Use this to retrieve workout history for users.",
)
