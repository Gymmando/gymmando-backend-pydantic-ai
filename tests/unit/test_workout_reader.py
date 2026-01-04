"""Unit tests for WorkoutReader agent."""

from unittest.mock import MagicMock, patch

from gymmando_graph.modules.workout.agents.workout_reader import WorkoutReader


class TestWorkoutReader:
    """Test suite for WorkoutReader class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_creates_reader(self):
            mock_loader = MagicMock()
            mock_loader.load_template.return_value = "Test template content"

            with patch(
                "gymmando_graph.modules.workout.agents.workout_reader.PromptTemplateLoader",
                return_value=mock_loader,
            ):
                with patch(
                    "gymmando_graph.modules.workout.agents.workout_reader.ChatOpenAI"
                ):
                    reader = WorkoutReader()

                    assert reader.prompt is not None
                    assert reader.llm is not None
                    assert reader.tools is not None
                    assert reader.llm_with_tools is not None
