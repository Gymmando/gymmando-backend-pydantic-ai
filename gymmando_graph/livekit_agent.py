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
from utils import Logger

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

    def __init__(self):
        """
        Initialize the Gymmando agent with default instructions.

        The agent is configured to be helpful and identify itself as "Gym-mando".
        """

        system_prompt = (PROMPTS_DIR / "main_llm_system_prompt.md").read_text()

        super().__init__(instructions=system_prompt)

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
        # TODO: Call workout graph with intent to route to PUT or GET path
        return f"Workout called with intent: {intent}"

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
            llm=groq.LLM(model="llama-3.1-8b-instant"),
            vad=silero.VAD.load(),
        )
        logger.info("✅ Agent session services configured successfully")
        logger.info("   - STT: Groq Whisper (whisper-large-v3-turbo)")
        logger.info("   - TTS: OpenAI (onyx voice)")
        logger.info("   - LLM: Groq Llama 3.1 8B Instant")
        logger.info("   - VAD: Silero")

        # Initialize the Gymmando agent
        logger.info("🤖 Initializing Gymmando agent...")
        gymmando = Gymmando()

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
