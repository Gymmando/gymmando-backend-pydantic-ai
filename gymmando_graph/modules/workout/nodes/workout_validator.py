class WorkoutValidator:
    """Validates workout data completeness."""

    REQUIRED_FIELDS = ["exercise", "sets", "reps", "weight"]

    def __init__(self):
        pass

    def validate(self, state: dict) -> dict:
        """
        Check if all required fields are present.

        Args:
            state: Current workout state

        Returns:
            Updated state with validation results
        """
        missing_fields = []

        for field in self.REQUIRED_FIELDS:
            value = state.get(field)
            if value is None or value == "":
                missing_fields.append(field)

        # Update state
        state["validation_status"] = "complete" if not missing_fields else "incomplete"
        state["missing_fields"] = missing_fields

        return state

    def is_complete(self, state: dict) -> bool:
        """Quick check if state is complete."""
        return all(state.get(field) for field in self.REQUIRED_FIELDS)
