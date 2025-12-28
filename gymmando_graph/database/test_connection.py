"""
Test script to verify Supabase connection and basic operations.
Run this from the gymmando_graph directory: python -m database.test_connection
"""

import uuid

from gymmando_graph.database import supabase
from gymmando_graph.utils import Logger

logger = Logger().get_logger()


def test_connection():
    """Test basic connection to Supabase."""
    logger.info("Testing Supabase connection...")

    try:
        # Test query - just check if we can connect
        response = (
            supabase.table("workouts").select("count", count="exact").limit(1).execute()
        )
        logger.info(f"Connection successful! Current workout count: {response.count}")
        return True
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False


def test_insert():
    """Test inserting a sample workout."""
    logger.info("Testing workout insertion...")

    test_workout = {
        "id": str(uuid.uuid4()),
        "user_id": "test_user",
        "exercise": "Squats",
        "sets": 3,
        "reps": 12,
        "weight": "135 lbs",
        "rest_time": 60,
        "comments": "Test workout from connection test",
        "intent": "put",
    }

    try:
        response = supabase.table("workouts").insert(test_workout).execute()
        logger.info(f"Insert successful! Workout ID: {response.data[0]['id']}")
        return response.data[0]
    except Exception as e:
        logger.error(f"Insert failed: {e}")
        return None


def test_select():
    """Test selecting workouts for a user."""
    logger.info("Testing workout selection...")

    try:
        response = (
            supabase.table("workouts")
            .select("*")
            .eq("user_id", "test_user")
            .limit(5)
            .execute()
        )
        logger.info(f"Found {len(response.data)} workouts for test_user")
        for workout in response.data:
            logger.info(
                f"  - {workout['exercise']}: {workout['sets']}x{workout['reps']} @ {workout['weight']}"
            )
        return response.data
    except Exception as e:
        logger.error(f"Select failed: {e}")
        return None


def test_delete_test_data():
    """Clean up test data."""
    logger.info("Cleaning up test data...")

    try:
        response = (
            supabase.table("workouts").delete().eq("user_id", "test_user").execute()
        )
        logger.info(f"Deleted {len(response.data)} test workouts")
        return True
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Supabase Connection Test")
    logger.info("=" * 60)

    # Test connection
    if not test_connection():
        logger.error("Cannot proceed - connection failed")
        exit(1)

    # Test insert
    inserted = test_insert()

    # Test select
    if inserted:
        test_select()

    # Clean up
    cleanup = input("\nDelete test data? (y/n): ")
    if cleanup.lower() == "y":
        test_delete_test_data()

    logger.info("=" * 60)
    logger.info("Test complete!")
    logger.info("=" * 60)
