"""Unit tests for workout Pydantic schemas."""


from gymmando_graph.modules.workout.schemas import WorkoutState


class TestWorkoutState:
    """Test suite for WorkoutState class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_with_required_fields(self):
            state = WorkoutState(user_input="squats 3x10", user_id="user123")

            assert state.user_input == "squats 3x10"
            assert state.user_id == "user123"
