"""Unit tests for database models."""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from gymmando_graph.database.models import WorkoutCreateModel, WorkoutDBModel


class TestWorkoutDBModel:
    """Test suite for WorkoutDBModel class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_with_required_fields(self):
            workout_id = uuid.uuid4()
            user_id = "user123"
            exercise = "squats"
            sets = 3
            reps = 10
            weight = "135 lbs"

            workout = WorkoutDBModel(
                id=workout_id,
                user_id=user_id,
                exercise=exercise,
                sets=sets,
                reps=reps,
                weight=weight,
            )

            assert workout.id == workout_id
            assert workout.user_id == user_id
            assert workout.exercise == exercise
            assert workout.sets == sets
            assert workout.reps == reps
            assert workout.weight == weight

        def test_init_with_optional_fields(self):
            workout_id = uuid.uuid4()
            created_at = datetime.utcnow()

            workout = WorkoutDBModel(
                id=workout_id,
                user_id="user123",
                exercise="squats",
                sets=3,
                reps=10,
                weight="135 lbs",
                rest_time=60,
                comments="Great workout!",
                created_at=created_at,
            )

            assert workout.rest_time == 60
            assert workout.comments == "Great workout!"
            assert workout.created_at == created_at

        def test_init_without_id_uses_default_factory(self):
            workout = WorkoutDBModel(
                user_id="user123",
                exercise="squats",
                sets=3,
                reps=10,
                weight="135 lbs",
            )

            assert workout.id is not None
            assert isinstance(workout.id, uuid.UUID)

        def test_init_without_created_at_uses_default_factory(self):
            workout = WorkoutDBModel(
                user_id="user123",
                exercise="squats",
                sets=3,
                reps=10,
                weight="135 lbs",
            )

            assert workout.created_at is not None
            assert isinstance(workout.created_at, datetime)

        def test_init_with_all_fields(self):
            workout_id = uuid.uuid4()
            created_at = datetime.utcnow()

            workout = WorkoutDBModel(
                id=workout_id,
                user_id="user123",
                exercise="bench press",
                sets=4,
                reps=8,
                weight="225 lbs",
                rest_time=90,
                comments="Heavy session",
                created_at=created_at,
            )

            assert workout.id == workout_id
            assert workout.user_id == "user123"
            assert workout.exercise == "bench press"
            assert workout.sets == 4
            assert workout.reps == 8
            assert workout.weight == "225 lbs"
            assert workout.rest_time == 90
            assert workout.comments == "Heavy session"
            assert workout.created_at == created_at

    class TestValidation:
        """Test validation methods."""

        def test_init_raises_error_missing_user_id(self):
            with pytest.raises(ValidationError):
                WorkoutDBModel(
                    exercise="squats",
                    sets=3,
                    reps=10,
                    weight="135 lbs",
                )

        def test_init_raises_error_missing_exercise(self):
            with pytest.raises(ValidationError):
                WorkoutDBModel(
                    user_id="user123",
                    sets=3,
                    reps=10,
                    weight="135 lbs",
                )

        def test_init_raises_error_missing_sets(self):
            with pytest.raises(ValidationError):
                WorkoutDBModel(
                    user_id="user123",
                    exercise="squats",
                    reps=10,
                    weight="135 lbs",
                )

        def test_init_raises_error_missing_reps(self):
            with pytest.raises(ValidationError):
                WorkoutDBModel(
                    user_id="user123",
                    exercise="squats",
                    sets=3,
                    weight="135 lbs",
                )

        def test_init_raises_error_missing_weight(self):
            with pytest.raises(ValidationError):
                WorkoutDBModel(
                    user_id="user123",
                    exercise="squats",
                    sets=3,
                    reps=10,
                )


class TestWorkoutCreateModel:
    """Test suite for WorkoutCreateModel class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_with_required_fields(self):
            workout = WorkoutCreateModel(
                user_id="user123",
                exercise="squats",
                sets=3,
                reps=10,
                weight="135 lbs",
            )

            assert workout.user_id == "user123"
            assert workout.exercise == "squats"
            assert workout.sets == 3
            assert workout.reps == 10
            assert workout.weight == "135 lbs"

        def test_init_with_optional_fields(self):
            workout = WorkoutCreateModel(
                user_id="user123",
                exercise="squats",
                sets=3,
                reps=10,
                weight="135 lbs",
                rest_time=60,
                comments="Great workout!",
            )

            assert workout.rest_time == 60
            assert workout.comments == "Great workout!"

        def test_init_without_optional_fields(self):
            workout = WorkoutCreateModel(
                user_id="user123",
                exercise="squats",
                sets=3,
                reps=10,
                weight="135 lbs",
            )

            assert workout.rest_time is None
            assert workout.comments is None

    class TestToDbDict:
        """Test to_db_dict method."""

        def test_to_db_dict_returns_dictionary(self):
            workout = WorkoutCreateModel(
                user_id="user123",
                exercise="squats",
                sets=3,
                reps=10,
                weight="135 lbs",
            )

            result = workout.to_db_dict()

            assert isinstance(result, dict)
            assert result["user_id"] == "user123"
            assert result["exercise"] == "squats"
            assert result["sets"] == 3
            assert result["reps"] == 10
            assert result["weight"] == "135 lbs"

        def test_to_db_dict_excludes_none_values(self):
            workout = WorkoutCreateModel(
                user_id="user123",
                exercise="squats",
                sets=3,
                reps=10,
                weight="135 lbs",
            )

            result = workout.to_db_dict()

            assert "rest_time" not in result
            assert "comments" not in result

        def test_to_db_dict_includes_all_provided_fields(self):
            workout = WorkoutCreateModel(
                user_id="user123",
                exercise="squats",
                sets=3,
                reps=10,
                weight="135 lbs",
                rest_time=60,
                comments="Great workout!",
            )

            result = workout.to_db_dict()

            assert result["rest_time"] == 60
            assert result["comments"] == "Great workout!"

    class TestValidation:
        """Test validation methods."""

        def test_init_raises_error_missing_user_id(self):
            with pytest.raises(ValidationError):
                WorkoutCreateModel(
                    exercise="squats",
                    sets=3,
                    reps=10,
                    weight="135 lbs",
                )

        def test_init_raises_error_missing_exercise(self):
            with pytest.raises(ValidationError):
                WorkoutCreateModel(
                    user_id="user123",
                    sets=3,
                    reps=10,
                    weight="135 lbs",
                )

        def test_init_raises_error_missing_sets(self):
            with pytest.raises(ValidationError):
                WorkoutCreateModel(
                    user_id="user123",
                    exercise="squats",
                    reps=10,
                    weight="135 lbs",
                )

        def test_init_raises_error_missing_reps(self):
            with pytest.raises(ValidationError):
                WorkoutCreateModel(
                    user_id="user123",
                    exercise="squats",
                    sets=3,
                    weight="135 lbs",
                )

        def test_init_raises_error_missing_weight(self):
            with pytest.raises(ValidationError):
                WorkoutCreateModel(
                    user_id="user123",
                    exercise="squats",
                    sets=3,
                    reps=10,
                )
