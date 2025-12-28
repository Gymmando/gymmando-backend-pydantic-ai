from typing import Literal, cast

from langgraph.graph import END, START, StateGraph

from gymmando_graph.modules.workout.agents import WorkoutParser
from gymmando_graph.modules.workout.nodes.workout_database import WorkoutDatabase
from gymmando_graph.modules.workout.nodes.workout_validator import WorkoutValidator
from gymmando_graph.modules.workout.schemas import WorkoutState
from gymmando_graph.utils import Logger


class WorkoutGraph:
    def __init__(self):
        # initialize logger
        self.logger = Logger().get_logger()
        # initialize the workout parser
        self.workout_parser = WorkoutParser()
        # initialize the validator
        self.validator = WorkoutValidator()
        # initialize the database service
        self.database = WorkoutDatabase()

        # create the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(WorkoutState)

        # add nodes
        workflow.add_node("workout_parser", self._workout_parser_node)
        workflow.add_node("workout_validator", self._workout_validator_node)
        workflow.add_node("workout_database", self._workout_database_node)

        # add edges
        workflow.add_edge(START, "workout_parser")
        workflow.add_edge("workout_parser", "workout_validator")
        workflow.add_conditional_edges(
            "workout_validator",
            self._should_save_to_database,
            {
                "database": "workout_database",
                "end": END,
            },
        )
        workflow.add_edge("workout_database", END)

        return workflow.compile()

    def _should_save_to_database(
        self, state: WorkoutState
    ) -> Literal["database", "end"]:
        """
        Determine if workout should be saved to database.

        Routes to database if:
        - intent is "put" (save operation)
        - validation_status is "complete" (all required fields present)

        Otherwise routes to end.
        """
        if state.intent == "put" and state.validation_status == "complete":
            return "database"
        return "end"

    def _workout_parser_node(self, state: WorkoutState) -> WorkoutState:
        """Parse user input and extract workout data."""
        # Process the user input through the parser
        parsed_result = self.workout_parser.process(state.user_input)

        # Update state with parsed workout data
        state.exercise = parsed_result.exercise
        state.sets = parsed_result.sets
        state.reps = parsed_result.reps
        state.weight = parsed_result.weight
        state.rest_time = parsed_result.rest_time
        state.comments = parsed_result.comments

        return state

    def _workout_validator_node(self, state: WorkoutState) -> WorkoutState:
        """Validate that all required workout fields are present."""
        return cast(WorkoutState, self.validator.validate(state))

    def _workout_database_node(self, state: WorkoutState) -> WorkoutState:
        """Save workout to database. Called only when validation is complete and intent is 'put'."""
        try:
            self.logger.info("Attempting to save workout to database...")
            saved_workout = self.database.save_workout(state)

            if saved_workout:
                self.logger.info(
                    f"Workout saved successfully with ID: {saved_workout.id}"
                )
                state.response = f"Workout saved! {state.exercise}: {state.sets}x{state.reps} @ {state.weight}"
            else:
                self.logger.error("Failed to save workout - database returned None")
                state.response = "Failed to save workout. Please try again."

        except ValueError as e:
            self.logger.error(f"Validation error while saving workout: {e}")
            state.response = f"Cannot save workout: {str(e)}"
        except Exception as e:
            self.logger.error(
                f"Unexpected error while saving workout: {e}", exc_info=True
            )
            state.response = (
                "An error occurred while saving your workout. Please try again."
            )

        return state

    def _handle_error(self, state):
        pass

    def run(self, state: WorkoutState) -> WorkoutState:
        """
        Run the workout graph with the given state using the compiled graph.

        Args:
            state: Initial WorkoutState with user input and intent

        Returns:
            Final WorkoutState after graph execution
        """
        self.logger.info(f"Running workout graph with intent: {state.intent}")
        # Convert state to dict for graph.invoke()
        state_dict = (
            state.model_dump() if hasattr(state, "model_dump") else state.dict()
        )
        result_dict = self.graph.invoke(state_dict)
        # Convert result back to WorkoutState
        result = WorkoutState(**result_dict)
        self.logger.info(f"Graph execution completed. Response: {result.response}")
        return result


if __name__ == "__main__":
    workout_graph = WorkoutGraph()
    state = WorkoutState(user_input="", user_id="test_user")

    workout_graph.logger.info("Workout Graph Test - Type 'exit' to quit")

    while True:
        user_input = input("Ask your question: ").strip()

        if user_input.lower() in ["exit", "quit", "q"]:
            workout_graph.logger.info("Exiting workout graph")
            break

        if not user_input:
            continue

        # Update state with new user input
        state.user_input = user_input

        # Run the graph
        state = workout_graph.run(state)

        workout_graph.logger.info("=" * 50)
