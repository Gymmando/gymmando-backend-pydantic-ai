"""Unit tests for WorkoutValidator class."""


from gymmando_graph.modules.workout.nodes.workout_validator import WorkoutValidator


class TestWorkoutValidator:
    """Test suite for WorkoutValidator class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_creates_validator(self):
            validator = WorkoutValidator()

            assert validator.REQUIRED_FIELDS == ["exercise", "sets", "reps", "weight"]
