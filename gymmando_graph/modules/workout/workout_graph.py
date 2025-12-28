from langgraph.graph import END, START, StateGraph

from gymmando_graph.modules.workout.agents import WorkoutParser
from gymmando_graph.modules.workout.schemas import WorkoutState


class WorkoutGraph:
    def __init__(self):
        # initialize the workout parser
        self.workout_parser = WorkoutParser()

        # create the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(WorkoutState)

        # add nodes

        # add conditional edges
        workflow.add_edge(START, END)

        return workflow.compile()

    def parser_node(self, state: WorkoutState) -> WorkoutState:
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

    def _validator_node(self, state):
        pass

    def _handle_error(self, state):
        pass

    def run(self):
        pass


if __name__ == "__main__":
    workout_graph = WorkoutGraph()
    state = WorkoutState(user_input="I did 3 sets of bench press", user_id="test_user")
    result = workout_graph.parser_node(state)
    print(result)
