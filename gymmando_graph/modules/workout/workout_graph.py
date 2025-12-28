from langgraph.graphs import StateGraph
from schemas import State


class WorkoutGraph:
    def __init__(self):
        # initialize the parser

        # create the graph
        pass

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph()

        # add nodes

        # add conditional edges

        return workflow.compile()

    def _parser_node(self, state: State):
        pass

    def _validator_node(self, state):
        pass

    def _handle_error(self, state):
        pass

    def run(self):
        pass
