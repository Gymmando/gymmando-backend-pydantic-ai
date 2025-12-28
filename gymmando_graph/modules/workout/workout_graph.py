from typing import cast

from langgraph.graph import START, StateGraph

from gymmando_graph.modules.workout.agents import WorkoutParser
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

        # create the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(WorkoutState)

        # add nodes
        workflow.add_node("workout_parser", self._workout_parser_node)
        workflow.add_node("workout_validator", self._workout_validator_node)

        # add conditional edges
        workflow.add_edge(START, "workout_parser")
        workflow.add_edge("workout_parser", "workout_validator")
        workflow.add_edge(START, "workout_validator")

        return workflow.compile()

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

    def _handle_error(self, state):
        pass

    def run(self, state: WorkoutState) -> WorkoutState:
        """Run the workout graph with the given state."""
        # Run parser node
        self.logger.info("--- Running Parser ---")
        state = self._workout_parser_node(state)
        self.logger.info(
            f"Parsed: exercise={state.exercise}, sets={state.sets}, reps={state.reps}, weight={state.weight}"
        )

        # Run validator node
        self.logger.info("--- Running Validator ---")
        state = self._workout_validator_node(state)
        self.logger.info(f"Validation Status: {state.validation_status}")
        if state.missing_fields:
            self.logger.warning(f"Missing Fields: {', '.join(state.missing_fields)}")
        else:
            self.logger.info("✅ All required fields present!")

        return state


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
