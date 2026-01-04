"""Unit tests for WorkoutGraph class."""

from unittest.mock import patch

from gymmando_graph.modules.workout.workout_graph import WorkoutGraph


class TestWorkoutGraph:
    """Test suite for WorkoutGraph class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_creates_graph(self):
            with patch("gymmando_graph.modules.workout.workout_graph.WorkoutParser"):
                with patch(
                    "gymmando_graph.modules.workout.workout_graph.WorkoutValidator"
                ):
                    with patch(
                        "gymmando_graph.modules.workout.workout_graph.WorkoutCRUD"
                    ):
                        with patch(
                            "gymmando_graph.modules.workout.workout_graph.WorkoutReader"
                        ):
                            with patch(
                                "gymmando_graph.modules.workout.workout_graph.StateGraph"
                            ):
                                graph = WorkoutGraph()

                                assert graph.workout_parser is not None
                                assert graph.validator is not None
                                assert graph.database is not None
                                assert graph.reader is not None
                                assert graph.graph is not None
