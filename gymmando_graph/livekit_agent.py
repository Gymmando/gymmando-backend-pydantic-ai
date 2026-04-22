"""LiveKit agent module for Gymmando voice assistant.

This module implements a LiveKit agent that provides voice-based interaction
with the Gymmando fitness assistant. The agent handles speech-to-text, text-to-speech,
and integrates with the workout graph for processing fitness-related queries.
"""

import json
import os
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
    """LiveKit agent for Gymmando fitness assistant.

    Extends LiveKit's Agent class to provide voice-based interaction with
    workout management functionality. Handles workout operations through
    the workout graph based on user voice commands.

    Attributes
    ----------
    workout_graph : WorkoutGraph
        Workout graph instance for processing workout operations.
    user_id : str
        Identifier for the current user.

    Examples
    --------
    The agent is typically instantiated by the entrypoint function when
    a LiveKit job is assigned. It processes voice input and responds with
    workout-related information.
    """

    def __init__(self, user_id: str = "default_user"):
        """Initialize the Gymmando agent.

        Loads the system prompt from markdown file and initializes the
        workout graph for processing user requests.

        Parameters
        ----------
        user_id : str, optional
            Identifier for the user (default: "default_user").
            Used to scope workout operations to the correct user.
        """
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
        """Process workout-related voice commands.

        Function tool that processes workout operations based on user voice
        input. Routes to appropriate workflow based on intent (get, put, delete).

        Parameters
        ----------
        context : RunContext
            LiveKit run context for the current agent session.
        transcript : str
            Transcribed text from user's voice input.
        intent : str
            Classified intent: "get" (read), "put" (create/update), or "delete".

        Returns
        -------
        str
            Response message to be spoken back to the user, containing workout
            data, confirmation, or error message.

        Notes
        -----
        For "get" intent, returns workout data directly.
        For "put" intent, returns validation status or confirmation.
        For "delete" intent, returns deletion confirmation.
        """
        logger.info(f"🏋️ Workout called - Intent: {intent}, User ID: {self.user_id}")
        state = WorkoutState(user_input=transcript, user_id=self.user_id, intent=intent)
        logger.info(f"📝 Created WorkoutState with user_id: {state.user_id}")
        try:
            state = self.workout_graph.run(state)

            # If state.response is already set (from update/delete/save operations), return it directly
            if state.response:
                logger.info(
                    f"✅ Returning response from graph: {state.response[:100]}..."
                )
                return state.response

            # Handle "get" intent - return the response directly (contains query results)
            if intent == "get":
                return state.response if state.response else "No workout data found."

            # Handle "put" intent - check validation status (for create operations)
            if intent == "put":
                if state.validation_status == "complete":
                    response = f"Logged: {state.exercise}, {state.sets}x{state.reps}."
                    if state.weight:
                        response += f" at {state.weight}."
                    return response + " Want to save it?"
                return f"Missing info: {', '.join(state.missing_fields)}."

            # Handle "delete" intent
            if intent == "delete":
                return (
                    state.response if state.response else "Delete operation completed."
                )

            # Fallback
            return state.response if state.response else "Operation completed."
        except Exception as e:
            logger.error(f"Error in workout tool: {e}", exc_info=True)
            return "Error processing workout data."


async def entrypoint(ctx: agents.JobContext):
    """Entrypoint function for LiveKit agent jobs.

    Initializes and starts the Gymmando agent session when a LiveKit job
    is assigned. Handles user identification, session setup, and greeting.

    Parameters
    ----------
    ctx : agents.JobContext
        LiveKit job context containing room and job information.

    Notes
    -----
    This function:
    1. Extracts user_id from room participants or metadata
    2. Initializes STT, TTS, LLM, and VAD services
    3. Creates and starts the Gymmando agent session
    4. Sends an initial greeting to the user

    The function attempts multiple strategies to identify the user:
    - From participant identity
    - From room metadata (JSON or string)
    - Falls back to "default_user" if not found
    """
    logger.info(f"🚀 Job Assigned: {ctx.job.id}")
    logger.info(f"📋 Room: {ctx.room.name}, Room ID: {ctx.room.sid}")
    logger.info(f"👥 Current participants in room: {len(ctx.room.remote_participants)}")

    # 1. GET USER ID FROM PARTICIPANT IDENTITY OR METADATA
    user_id = "default_user"

    # Helper function to extract user_id from participants
    def extract_user_id_from_participants():
        nonlocal user_id
        try:
            logger.info(f"🔍 Checking room participants...")
            logger.info(
                f"   Remote participants count: {len(ctx.room.remote_participants)}"
            )

            # Log all participant identities for debugging
            for sid, participant in ctx.room.remote_participants.items():
                logger.info(
                    f"   Participant SID: {sid}, Identity: {participant.identity}"
                )
                if participant.identity and participant.identity != "agent":
                    user_id = participant.identity
                    logger.info(f"✅ Found user_id from participant identity: {user_id}")
                    return user_id
        except Exception as e:
            logger.warning(f"Error checking participants: {e}")
        return None

    try:
        await ctx.connect()  # Connect to get room participants

        # Try to get user_id from participants immediately
        extract_user_id_from_participants()

        # If not found, wait a bit and try again (participant might join after agent)
        if user_id == "default_user":
            import asyncio

            await asyncio.sleep(1)  # Wait 1 second for participant to join
            extract_user_id_from_participants()

        # Fallback: try metadata if identity not found
        if user_id == "default_user":
            metadata_raw = ctx.room.metadata
            logger.info(f"🔍 Checking room metadata: {metadata_raw}")
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
                if user_id != "default_user":
                    logger.info(f"✅ Found user_id from metadata: {user_id}")
    except Exception as e:
        logger.warning(f"User ID parse failed: {e}. Using default_user.", exc_info=True)

    logger.info(f"👤 Using user_id: {user_id}")

    # 2. ROBUST GREETING LOAD
    greeting_path = PROMPTS_DIR / "main_llm_greeting_prompt.md"
    greeting_prompt = (
        greeting_path.read_text()
        if greeting_path.exists()
        else "Hello! I am Gymmando. How can I help you today?"
    )

    try:
        logger.info("⚙️  Starting session services...")

        # Check if OpenAI API key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            logger.warning("⚠️ OPENAI_API_KEY not found in environment variables")
        else:
            logger.info(f"✅ OPENAI_API_KEY found (length: {len(openai_key)})")

        logger.info("🔧 Initializing TTS service...")
        tts_service = openai.TTS(voice="onyx")
        logger.info("✅ TTS service initialized")

        session = AgentSession(
            stt=openai.STT(model="whisper-1"),
            # stt=groq.STT(model="whisper-large-v3-turbo"),
            tts=tts_service,
            llm=openai.LLM(model="gpt-4o-mini"),
            vad=silero.VAD.load(force_cpu=True),
        )
        logger.info("✅ AgentSession created")

        gymmando = Gymmando(user_id=user_id)

        # Connect to the room
        logger.info("🔌 Connecting session to room...")
        await session.start(
            room=ctx.room,
            agent=gymmando,
            room_input_options=RoomInputOptions(close_on_disconnect=False),
        )

        logger.info(f"✅ Session active in room: {ctx.room.name}")

        # Check participants again after session starts (participant might have joined)
        import asyncio

        await asyncio.sleep(0.5)  # Brief wait for participant to fully connect
        extract_user_id_from_participants()

        # Update gymmando's user_id if we found it
        if user_id != "default_user":
            gymmando.user_id = user_id
            logger.info(f"✅ Final user_id after session start: {user_id}")
        else:
            logger.warning(
                f"⚠️ Still using default_user - no participant identity found"
            )

        # 3. GENERATE INITIAL GREETING
        logger.info(f"🎤 Generating greeting with prompt: {greeting_prompt[:50]}...")
        try:
            await session.generate_reply(instructions=greeting_prompt)
            logger.info("👋 Greeting sent successfully.")
        except Exception as greeting_error:
            logger.error(
                f"❌ Failed to generate greeting: {greeting_error}", exc_info=True
            )

    except Exception as e:
        logger.error(f"❌ Agent error: {str(e)}", exc_info=True)
        # In a real app, you might want to ctx.shutdown() here


if __name__ == "__main__":
    logger.info("🎬 Starting Gymmando Worker...")

    # Log environment variables for debugging (without exposing secrets)
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_key = os.getenv("LIVEKIT_API_KEY")
    livekit_secret = os.getenv("LIVEKIT_API_SECRET")
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    logger.info(f"🔍 Environment check:")
    logger.info(
        f"  LIVEKIT_URL: {'✅ Set' if livekit_url else '❌ Missing'} ({livekit_url if livekit_url else 'N/A'})"
    )
    logger.info(
        f"  LIVEKIT_API_KEY: {'✅ Set' if livekit_key else '❌ Missing'} (length: {len(livekit_key) if livekit_key else 0})"
    )
    logger.info(
        f"  LIVEKIT_API_SECRET: {'✅ Set' if livekit_secret else '❌ Missing'} (length: {len(livekit_secret) if livekit_secret else 0})"
    )
    logger.info(
        f"  OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'} (length: {len(openai_key) if openai_key else 0})"
    )
    logger.info(
        f"  GROQ_API_KEY: {'✅ Set' if groq_key else '❌ Missing'} (length: {len(groq_key) if groq_key else 0})"
    )

    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
