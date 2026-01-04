"""Unit tests for WorkoutParser agent."""

from unittest.mock import MagicMock, patch

from gymmando_graph.modules.workout.agents.workout_parser import WorkoutParser


class TestWorkoutParser:
    """Test suite for WorkoutParser class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_creates_parser(self):
            mock_loader = MagicMock()
            mock_loader.load_template.return_value = "Test template content"

            with patch(
                "gymmando_graph.modules.workout.agents.workout_parser.PromptTemplateLoader",
                return_value=mock_loader,
            ):
                with patch(
                    "gymmando_graph.modules.workout.agents.workout_parser.ChatOpenAI"
                ):
                    parser = WorkoutParser()

                    assert parser.parser is not None
                    assert parser.prompt is not None
                    assert parser.llm is not None
                    assert parser.chain is not None
