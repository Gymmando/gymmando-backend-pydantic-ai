from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI

from gymmando_graph.modules.workout.nodes.workout_query_tools import query_workouts
from gymmando_graph.utils import PromptTemplateLoader

load_dotenv()


class WorkoutRetrieverAgent:
    def __init__(self):
        # Initialize the prompt
        # Get the prompt templates directory relative to this file
        prompts_dir = Path(__file__).parent.parent / "prompt_templates"
        ptl = PromptTemplateLoader(str(prompts_dir))
        system_template = ptl.load_template(
            "workout_retriever_prompt_template_system.md"
        )
        human_template = ptl.load_template("workout_retriever_prompt_template_human.md")
        system_message = SystemMessagePromptTemplate.from_template(
            template=system_template
        )
        human_message = HumanMessagePromptTemplate.from_template(
            template=human_template, input_variables=["user_query", "user_id"]
        )

        self.prompt = ChatPromptTemplate.from_messages([system_message, human_message])

        # Initialize the LLM with tools
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = [query_workouts]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def retrieve(self, user_query: str, user_id: str) -> str:
        """
        Process a user query and retrieve relevant workout data.

        Args:
            user_query: Natural language query from the user
            user_id: User ID to filter workouts

        Returns:
            JSON string of workout data (no second LLM call)
        """
        from gymmando_graph.utils import Logger

        logger = Logger().get_logger()

        # Format the prompt
        messages = list(
            self.prompt.format_messages(user_query=user_query, user_id=user_id)
        )

        # Get LLM response with tool calls
        response = self.llm_with_tools.invoke(messages)

        logger.info(f"LLM response: {response}")
        logger.info(f"Tool calls: {getattr(response, 'tool_calls', None)}")

        # Check if LLM wants to call a tool
        if hasattr(response, "tool_calls") and response.tool_calls:
            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_args["user_id"] = user_id  # Always add user_id

                logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

                # Call the tool and return result directly
                if tool_name == "query_workouts":
                    tool_result = query_workouts.invoke(tool_args)
                    logger.info(f"Tool result: {tool_result}")
                    return str(tool_result)

        # If no tool call, return LLM response
        logger.warning("No tool call detected in LLM response")
        if hasattr(response, "content") and response.content:
            return str(response.content)
        return str(response)


if __name__ == "__main__":
    from gymmando_graph.database import get_supabase_client

    # First, let's check what's actually in the database
    print("=" * 60)
    print("Checking database contents...")
    print("=" * 60)
    client = get_supabase_client()

    # Get all workouts to see what user_ids and exercises exist
    all_workouts = client.table("workouts").select("*").limit(20).execute()
    print(f"Total workouts in DB: {len(all_workouts.data)}")
    if all_workouts.data:
        print("\nSample workouts:")
        for workout in all_workouts.data[:5]:
            print(
                f"  - user_id: {workout.get('user_id')}, exercise: {workout.get('exercise')}, created: {workout.get('created_at')}"
            )
    print("=" * 60)
    print()

    # Now test the agent
    agent = WorkoutRetrieverAgent()

    # Test 1: Check if any workouts exist for the user (no exercise filter)
    print("Test 1: Getting any workouts for user...")
    result = agent.retrieve("Show me my workouts", user_id="default_user")
    print(f"Result: {result}\n")

    # Test 2: Query with specific exercise
    print("Test 2: Getting last lunges workout...")
    result = agent.retrieve(
        "What was my last 2 lunges workout?", user_id="default_user"
    )
    print(f"Result: {result}")
