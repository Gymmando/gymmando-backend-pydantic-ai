from typing import Literal, cast

from langgraph.graph import END, START, StateGraph

from gymmando_graph.modules.workout.agents import WorkoutParser, WorkoutRetriever
from gymmando_graph.modules.workout.crud import WorkoutCRUD
from gymmando_graph.modules.workout.nodes.workout_validator import WorkoutValidator
from gymmando_graph.modules.workout.schemas import WorkoutState
from gymmando_graph.utils import Logger

logger = Logger().get_logger()


class WorkoutGraph:
    def __init__(self):
        # initialize the workout parser
        self.workout_parser = WorkoutParser()
        # initialize the validator
        self.validator = WorkoutValidator()
        # initialize the database service
        self.database = WorkoutCRUD()
        # initialize the retriever agent
        self.retriever = WorkoutRetriever()

        # create the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(WorkoutState)

        # add nodes
        workflow.add_node("workout_parser", self._workout_parser_node)
        workflow.add_node("workout_validator", self._workout_validator_node)
        workflow.add_node("workout_creator", self._workout_creator_node)
        workflow.add_node("workout_reader", self._workout_reader_node)

        # add edges
        workflow.add_edge(START, "workout_parser")
        # Route based on intent: get -> reader, put -> validator
        workflow.add_conditional_edges(
            "workout_parser",
            self._route_by_intent,
            {
                "reader": "workout_reader",
                "validator": "workout_validator",
            },
        )
        workflow.add_edge("workout_reader", END)
        workflow.add_conditional_edges(
            "workout_validator",
            self._should_save_to_database,
            {
                "database": "workout_creator",
                "end": END,
            },
        )
        workflow.add_edge("workout_creator", END)

        return workflow.compile()

    def _route_by_intent(self, state: WorkoutState) -> Literal["reader", "validator"]:
        """
        Route based on intent after parsing.

        Routes to reader if intent is "get" (read operation).
        Routes to validator if intent is "put" (create operation).
        """
        if state.intent == "get":
            return "reader"
        return "validator"

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

    def _workout_reader_node(self, state: WorkoutState) -> WorkoutState:
        """Read workout data based on user query."""
        try:
            logger.info(f"Retrieving workouts for user: {state.user_id}")
            result = self.retriever.retrieve(state.user_input, state.user_id)
            state.response = result
            logger.info("Workout retrieval completed successfully")
        except Exception as e:
            logger.error(f"Error retrieving workouts: {e}", exc_info=True)
            state.response = "Sorry, I encountered an error retrieving your workouts. Please try again."
        return state

    def _workout_validator_node(self, state: WorkoutState) -> WorkoutState:
        """Validate that all required workout fields are present."""
        return cast(WorkoutState, self.validator.validate(state))

    def _workout_creator_node(self, state: WorkoutState) -> WorkoutState:
        """Create workout in database. Called only when validation is complete and intent is 'put'."""
        try:
            logger.info("Attempting to save workout to database...")
            saved_workout = self.database.create(state)

            if saved_workout:
                logger.info(f"Workout saved successfully with ID: {saved_workout.id}")
                state.response = f"Workout saved! {state.exercise}: {state.sets}x{state.reps} @ {state.weight}"
            else:
                logger.error("Failed to save workout - database returned None")
                state.response = "Failed to save workout. Please try again."

        except ValueError as e:
            logger.error(f"Validation error while saving workout: {e}")
            state.response = f"Cannot save workout: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error while saving workout: {e}", exc_info=True)
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
        logger.info(f"Running workout graph with intent: {state.intent}")
        # Convert state to dict for graph.invoke()
        state_dict = (
            state.model_dump() if hasattr(state, "model_dump") else state.dict()
        )
        result_dict = self.graph.invoke(state_dict)
        # Convert result back to WorkoutState
        result = WorkoutState(**result_dict)
        logger.info(f"Graph execution completed. Response: {result.response}")
        return result


if __name__ == "__main__":
    workout_graph = WorkoutGraph()
    state = WorkoutState(user_input="", user_id="test_user")

    logger.info("Workout Graph Test - Type 'exit' to quit")

    while True:
        user_input = input("Ask your question: ").strip()

        if user_input.lower() in ["exit", "quit", "q"]:
            logger.info("Exiting workout graph")
            break

        if not user_input:
            continue

        # Update state with new user input
        state.user_input = user_input

        # Run the graph
        state = workout_graph.run(state)

        logger.info("=" * 50)
