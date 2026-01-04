import json
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from gymmando_graph.modules.workout.crud import WorkoutCRUD
from gymmando_graph.utils import Logger, PromptTemplateLoader

load_dotenv()

logger = Logger().get_logger()

# Initialize WorkoutCRUD instance
_workout_crud = WorkoutCRUD()


def _query_workouts_impl(
    user_id: str,
    exercise: Optional[str] = None,
    exercise_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 10,
    order_by: Optional[str] = "created_at",
    order_direction: Optional[str] = "desc",
) -> str:
    """
    Query workouts from the database based on various filters.

    Args:
        user_id: The user ID to filter workouts by (required)
        exercise: Filter by specific exercise name (e.g., "squats", "bench press")
        exercise_type: Filter by exercise type/category (e.g., "legs", "chest", "arms")
        start_date: Start date for date range filter (YYYY-MM-DD format)
        end_date: End date for date range filter (YYYY-MM-DD format)
        limit: Maximum number of workouts to return (default: 10)
        order_by: Field to order by (default: "created_at")
        order_direction: Order direction - "asc" or "desc" (default: "desc")

    Returns:
        JSON string of workout data matching the query
    """
    try:
        logger.info(
            f"🔍 Querying workouts from Supabase with params: user_id={user_id}, exercise={exercise}, limit={limit}"
        )

        # Use WorkoutCRUD to query workouts
        workouts = _workout_crud.query(
            user_id=user_id,
            exercise=exercise,
            exercise_type=exercise_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            order_by=order_by,
            order_direction=order_direction,
        )

        logger.info(f"Query returned {len(workouts)} workouts")

        if workouts:
            # Convert to JSON string for LLM consumption
            workouts_dict = [workout.model_dump() for workout in workouts]
            return json.dumps(workouts_dict, default=str)

        return json.dumps([])

    except Exception as e:
        logger.error(f"Failed to query workouts: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


# Create the LangChain tool
query_workouts = StructuredTool.from_function(
    func=_query_workouts_impl,
    name="query_workouts",
    description="Query workouts from the database based on various filters. Use this to retrieve workout history for users.",
)


class WorkoutRetriever:
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
    agent = WorkoutRetriever()

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
