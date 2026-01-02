import json
from pathlib import Path

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions, RunContext
from livekit.agents.llm import function_tool
from livekit.plugins import groq, openai, silero

from gymmando_graph.modules.workout.schemas import WorkoutState
from gymmando_graph.modules.workout.workout_graph import WorkoutGraph
from gymmando_graph.utils import Logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = Logger().get_logger()

# Get project root directory
PROJECT_ROOT = Path(__file__).parent
PROMPTS_DIR = PROJECT_ROOT / "livekit_agent_prompt_templates"


class Gymmando(Agent):
    def __init__(self, user_id: str = "default_user"):
        # ROBUST PATH CHECK
        prompt_path = PROMPTS_DIR / "main_llm_system_prompt.md"
        if prompt_path.exists():
            system_prompt = prompt_path.read_text()
        else:
            logger.error(f"❌ System prompt NOT FOUND at {prompt_path}")
            system_prompt = "You are Gymmando, a helpful fitness assistant."

        super().__init__(instructions=system_prompt)
        self.workout_graph = WorkoutGraph()
        self.user_id = user_id
        logger.info(f"✅ Gymmando agent initialized for user: {user_id}")

    @function_tool
    async def workout(self, context: RunContext, transcript: str, intent: str) -> str:
        logger.info(f"🏋️ Workout called - Intent: {intent}")
        state = WorkoutState(user_input=transcript, user_id=self.user_id, intent=intent)
        try:
            state = self.workout_graph.run(state)

            # Handle "get" intent - return the response directly (contains query results)
            if intent == "get":
                return state.response if state.response else "No workout data found."

            # Handle "put" intent - check validation status
            if state.validation_status == "complete":
                response = f"Logged: {state.exercise}, {state.sets}x{state.reps}."
                if state.weight:
                    response += f" at {state.weight}."
                return response + " Want to save it?"
            return f"Missing info: {', '.join(state.missing_fields)}."
        except Exception as e:
            logger.error(f"Error in workout tool: {e}", exc_info=True)
            return "Error processing workout data."


async def entrypoint(ctx: agents.JobContext):
    logger.info(f"🚀 Job Assigned: {ctx.job.id}")

    # 1. SAFELY PARSE USER ID FROM METADATA
    user_id = "default_user"
    try:
        metadata_raw = ctx.room.metadata
        if metadata_raw:
            # If it's a string, try to parse JSON
            if isinstance(metadata_raw, str):
                try:
                    data = json.loads(metadata_raw)
                    user_id = data.get("user_id", "default_user")
                except json.JSONDecodeError:
                    # If it's just a raw string like "user123"
                    user_id = metadata_raw
            elif isinstance(metadata_raw, dict):
                user_id = metadata_raw.get("user_id", "default_user")
    except Exception as e:
        logger.warning(f"Metadata parse failed: {e}. Using default_user.")

    # 2. ROBUST GREETING LOAD
    greeting_path = PROMPTS_DIR / "main_llm_greeting_prompt.md"
    greeting_prompt = (
        greeting_path.read_text()
        if greeting_path.exists()
        else "Hello! I am Gymmando. How can I help you today?"
    )

    try:
        logger.info("⚙️  Starting session services...")
        session = AgentSession(
            stt=groq.STT(model="whisper-large-v3-turbo"),
            tts=openai.TTS(voice="onyx"),
            llm=openai.LLM(model="gpt-4o-mini"),
            vad=silero.VAD.load(force_cpu=True),
        )

        gymmando = Gymmando(user_id=user_id)

        # Connect to the room
        await session.start(
            room=ctx.room,
            agent=gymmando,
            room_input_options=RoomInputOptions(close_on_disconnect=False),
        )

        logger.info(f"✅ Session active in room: {ctx.room.name}")

        # 3. GENERATE INITIAL GREETING
        await session.generate_reply(instructions=greeting_prompt)
        logger.info("👋 Greeting sent.")

    except Exception as e:
        logger.error(f"❌ Agent error: {str(e)}", exc_info=True)
        # In a real app, you might want to ctx.shutdown() here


if __name__ == "__main__":
    logger.info("🎬 Starting Gymmando Worker...")
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
