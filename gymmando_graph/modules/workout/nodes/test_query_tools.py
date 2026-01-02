"""
Test script for workout query tools.
Run from gymmando_graph directory: python -m modules.workout.nodes.test_query_tools
"""

import json

from gymmando_graph.database import get_supabase_client
from gymmando_graph.modules.workout.nodes.workout_query_tools import query_workouts


def test_query_all():
    """Test querying all workouts for a user."""
    print("=" * 60)
    print("Test 1: Query all workouts (no filters)")
    print("=" * 60)

    # First, let's see what user_ids exist
    client = get_supabase_client()
    all_workouts = (
        client.table("workouts").select("user_id, exercise").limit(10).execute()
    )

    if not all_workouts.data:
        print("No workouts found in database!")
        return

    # Get a user_id from existing data
    test_user_id = all_workouts.data[0]["user_id"]
    print(f"Testing with user_id: {test_user_id}")
    print(f"Found {len(all_workouts.data)} sample workouts")
    print("\nSample workouts:")
    for w in all_workouts.data[:5]:
        print(f"  - user_id: {w['user_id']}, exercise: {w['exercise']}")

    # Test query without filters
    result = query_workouts.invoke({"user_id": test_user_id})
    workouts = json.loads(result)
    print(f"\nQuery returned {len(workouts)} workouts")
    if workouts:
        print("Sample result:")
        print(json.dumps(workouts[0], indent=2))
    print()


def test_query_with_exercise():
    """Test querying with exercise filter."""
    print("=" * 60)
    print("Test 2: Query with exercise filter")
    print("=" * 60)

    # Get a user_id and exercise from existing data
    client = get_supabase_client()
    all_workouts = (
        client.table("workouts").select("user_id, exercise").limit(20).execute()
    )

    if not all_workouts.data:
        print("No workouts found in database!")
        return

    test_user_id = all_workouts.data[0]["user_id"]
    test_exercise = all_workouts.data[0]["exercise"]

    print(f"Testing with user_id: {test_user_id}")
    print(f"Testing with exercise: {test_exercise}")

    # Test query with exercise filter
    result = query_workouts.invoke({"user_id": test_user_id, "exercise": test_exercise})
    workouts = json.loads(result)
    print(f"\nQuery returned {len(workouts)} workouts")
    if workouts:
        print("Sample result:")
        print(json.dumps(workouts[0], indent=2))
    print()


def test_query_with_limit():
    """Test querying with limit."""
    print("=" * 60)
    print("Test 3: Query with limit")
    print("=" * 60)

    # Get a user_id from existing data
    client = get_supabase_client()
    all_workouts = client.table("workouts").select("user_id").limit(1).execute()

    if not all_workouts.data:
        print("No workouts found in database!")
        return

    test_user_id = all_workouts.data[0]["user_id"]

    print(f"Testing with user_id: {test_user_id}, limit: 3")

    # Test query with limit
    result = query_workouts.invoke({"user_id": test_user_id, "limit": 3})
    workouts = json.loads(result)
    print(f"\nQuery returned {len(workouts)} workouts (expected max 3)")
    if workouts:
        print("Results:")
        for w in workouts:
            print(
                f"  - {w.get('exercise')}: {w.get('sets')}x{w.get('reps')} @ {w.get('weight')}"
            )
    print()


if __name__ == "__main__":
    try:
        test_query_all()
        test_query_with_exercise()
        test_query_with_limit()
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
