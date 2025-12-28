"""
LiveKit Agent Entry Point for Gymmando Voice Assistant

This module provides the main entry point for the Gymmando voice assistant agent.
It configures the LiveKit agent session with speech-to-text, text-to-speech,
language model, and voice activity detection services.

The agent uses:
- Groq Whisper for speech-to-text (STT)
- OpenAI TTS for text-to-speech (voice: onyx)
- Groq Llama 3.1 8B Instant for language model (LLM)
- Silero for voice activity detection (VAD)
"""

from pathlib import Path

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RunContext
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
    """
    Gymmando Voice Assistant Agent

    A conversational agent designed to assist users with gym-related queries
    and workout tracking through voice interactions.

    Attributes:
        instructions (str): System instructions defining the agent's behavior
                           and personality as a helpful gym assistant.
    """

    def __init__(self, user_id: str = "default_user"):
        """
        Initialize the Gymmando agent with default instructions.

        The agent is configured to be helpful and identify itself as "Gym-mando".

        Args:
            user_id: User identifier for tracking workouts and personalization
        """

        system_prompt = (PROMPTS_DIR / "main_llm_system_prompt.md").read_text()

        super().__init__(instructions=system_prompt)

        # Initialize workout graph
        self.workout_graph = WorkoutGraph()
        self.user_id = user_id

        logger.info("✅ Gymmando agent initialized")

    @function_tool
    async def workout(self, context: RunContext, transcript: str, intent: str) -> str:
        """
        Handle workout-related requests. Use this for exercise-related queries.

        Args:
            transcript: The user's message about workouts
            intent: Either 'put' to store workout data or 'get' to retrieve workout history
        """
        logger.info(
            f"🏋️ Workout function called - Intent: {intent}, Transcript: {transcript}"
        )

        # Create workout state from user input
        state = WorkoutState(user_input=transcript, user_id=self.user_id, intent=intent)

        # Run the workout graph
        try:
            state = self.workout_graph.run(state)

            # Generate response based on validation status
            if state.validation_status == "complete":
                response = f"Got it! I've logged: {state.exercise}, {state.sets} sets, {state.reps} reps"
                if state.weight:
                    response += f", {state.weight}"
                response += ". Would you like to save this workout?"
            else:
                missing = ", ".join(state.missing_fields)
                response = f"I need a bit more info. Could you tell me the {missing}?"

            return response
        except Exception as e:
            logger.error(f"Error processing workout: {e}", exc_info=True)
            return "Sorry, I encountered an error processing your workout. Could you try again?"

    @function_tool
    async def nutrition(self, context: RunContext, transcript: str, intent: str) -> str:
        """
        Handle nutrition-related requests. Use this for food/diet-related queries.

        Args:
            transcript: The user's message about nutrition
            intent: Either 'put' to store meal data or 'get' to retrieve nutrition info
        """
        logger.info(
            f"🍗 Nutrition function called - Intent: {intent}, Transcript: {transcript}"
        )
        # TODO: Call nutrition graph with intent to route to PUT or GET path
        return f"Nutrition called with intent: {intent}"

    @function_tool
    async def measurements(
        self, context: RunContext, transcript: str, intent: str
    ) -> str:
        """
        Handle body measurement requests. Use this for weight/body tracking queries.

        Args:
            transcript: The user's message about measurements
            intent: Either 'put' to store measurement data or 'get' to retrieve measurement history
        """
        logger.info(
            f"📏 Measurements function called - Intent: {intent}, Transcript: {transcript}"
        )
        # TODO: Call measurements graph with intent to route to PUT or GET path
        return f"Measurements called with intent: {intent}"


async def entrypoint(ctx: agents.JobContext):
    """
    LiveKit agent entry point function.

    This is the main entry point called by LiveKit when a new agent job starts.
    It sets up the agent session with all required services (STT, TTS, LLM, VAD)
    and starts the conversation with a greeting.

    Args:
        ctx (agents.JobContext): The LiveKit job context containing room information
                                 and other job metadata.

    Configuration:
        - STT: Groq Whisper (whisper-large-v3-turbo) for speech recognition
        - TTS: OpenAI TTS with "onyx" voice for natural speech synthesis
        - LLM: Groq Llama 3.1 8B Instant for fast, cost-effective language processing
        - VAD: Silero VAD for voice activity detection (speech/silence detection)
    """
    logger.info("🚀 Starting Gymmando agent session")
    logger.info(f"📍 Room: {ctx.room.name if ctx.room else 'N/A'}")

    # Load greeting prompt directly
    greeting_prompt = (PROMPTS_DIR / "main_llm_greeting_prompt.md").read_text()

    try:
        # Configure agent session with all required services
        logger.info("⚙️  Configuring agent session services...")
        session = AgentSession(
            stt=groq.STT(model="whisper-large-v3-turbo"),
            tts=openai.TTS(voice="onyx"),
            llm=openai.LLM(
                model="gpt-4o-mini"
            ),  # Using OpenAI to avoid Groq rate limits
            vad=silero.VAD.load(),
        )
        logger.info("✅ Agent session services configured successfully")
        logger.info("   - STT: Groq Whisper (whisper-large-v3-turbo)")
        logger.info("   - TTS: OpenAI (onyx voice)")
        logger.info("   - LLM: OpenAI GPT-4o-mini")
        logger.info("   - VAD: Silero")

        # Initialize the Gymmando agent
        logger.info("🤖 Initializing Gymmando agent...")
        # Extract user_id from room metadata or use default
        user_id = (
            ctx.room.metadata.get("user_id")
            if ctx.room and ctx.room.metadata
            else "default_user"
        )
        gymmando = Gymmando(user_id=user_id)

        # Start the agent session with the room
        logger.info("🎯 Starting agent session with room...")
        await session.start(room=ctx.room, agent=gymmando)
        logger.info("✅ Agent session started successfully")

        # Generate initial greeting
        logger.info("👋 Generating greeting message...")
        await session.generate_reply(instructions=greeting_prompt)
        logger.info("✅ Greeting sent, agent is ready for conversation")

    except Exception as e:
        logger.error(f"❌ Error during agent initialization: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    """
    Main entry point when running the agent directly.

    Starts the LiveKit agent worker with the entrypoint function.
    """
    logger.info("🎬 Starting Gymmando LiveKit agent worker...")
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
