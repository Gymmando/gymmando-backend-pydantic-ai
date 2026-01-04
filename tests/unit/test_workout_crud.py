"""Unit tests for WorkoutCRUD class."""


from gymmando_graph.modules.workout.crud import WorkoutCRUD


class TestWorkoutCRUD:
    """Test suite for WorkoutCRUD class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_creates_crud_instance(self):
            crud = WorkoutCRUD()

            assert crud.table_name == "workouts"
