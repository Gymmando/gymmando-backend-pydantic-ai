"""Integration tests for OpenAI API calls.

These tests use real OpenAI API calls and should only be run explicitly.
Run with: pytest tests/integration/test_openai_integration.py -m real_ai
"""

import os

import pytest

from gymmando_graph.modules.workout.agents.workout_parser import WorkoutParser


@pytest.mark.integration
@pytest.mark.real_ai
class TestOpenAIIntegration:
    """Integration tests for OpenAI API with WorkoutParser."""

    class TestWorkoutParserRealAI:
        """Test WorkoutParser with real OpenAI API calls."""

        def test_parser_real_ai_simple_workout(self):
            """Test parser with real OpenAI API for simple workout input."""
            # Skip if OpenAI API key is not set
            if not os.getenv("OPENAI_API_KEY"):
                pytest.skip("OPENAI_API_KEY not set")

            parser = WorkoutParser()
            user_input = "Squats 3 sets of 10 reps at 135 lbs"

            result = parser.process(user_input)

            # Verify result is not None
            assert result is not None

            # Verify required fields are extracted
            assert result.exercise is not None
            assert result.sets is not None
            assert result.reps is not None
            assert result.weight is not None

            # Verify extracted values
            assert "squat" in result.exercise.lower()
            assert result.sets == 3
            assert result.reps == 10
            assert "135" in result.weight.lower() or "lbs" in result.weight.lower()
