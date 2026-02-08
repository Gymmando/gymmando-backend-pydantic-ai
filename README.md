# Gymmando Backend

A voice-driven workout logging assistant powered by AI. Speak your workouts naturally, and Gymmando transcribes, parses, validates, and saves them automatically.

## Overview

Gymmando uses real-time voice sessions to capture workout data. The backend combines LiveKit for voice handling, LangGraph for workflow orchestration, and LLMs for natural language understanding to transform spoken input into structured workout logs.

## Core Features

- **Voice-First Interface**: Real-time transcription and natural language processing
- **Smart Parsing**: Extracts exercise name, sets, reps, weight, rest time, and comments from spoken input
- **Intelligent Intent Routing**: Automatically detects whether you want to create, read, update, or delete workouts
- **Auto-Context**: Updates or deletes your most recent workout when no specific ID is mentioned
- **Data Validation**: Ensures required fields are present before saving
- **User-Scoped Storage**: All workouts are isolated by user ID

## Tech Stack

- **API**: FastAPI
- **Voice Sessions**: LiveKit
- **Workflow Engine**: LangGraph
- **LLMs**: OpenAI GPT-4o-mini (parsing & reading), Groq Whisper (STT), OpenAI TTS
- **Database**: Supabase (PostgreSQL)
- **Models**: Pydantic for data validation

## Architecture

```
Voice Input (LiveKit)
    ↓
Transcription (Groq Whisper)
    ↓
LiveKit Agent → workout() tool
    ↓
LangGraph Workflow:
    Parser → Intent Router → [Reader|Updator|Deletor|Validator] → Saver
    ↓
Supabase (workouts table)
```

## Project Structure

```
gymmando-backend/
├── gymmando_api/          # FastAPI application
│   ├── main.py           # App entry point, /token endpoint
│   └── routes/           # API routes (auth, health, livekit - stubbed)
├── gymmando_graph/        # LangGraph workflows
│   ├── livekit_agent.py  # Voice session handler
│   ├── database/         # Supabase client & models
│   └── modules/
│       ├── workout/      # Workout workflow (functional)
│       │   ├── workout_graph.py
│       │   ├── agents/   # Parser & Reader LLM agents
│       │   ├── nodes/    # Graph nodes (validator, saver, etc.)
│       │   ├── crud.py   # Database operations
│       │   └── schemas/  # Pydantic models
│       ├── nutrition/    # Nutrition tracking (stubbed)
│       └── measurements/ # Body measurements (stubbed)
└── requirements.txt
```

## How It Works

### 1. Voice Session Flow
- User connects to LiveKit room
- Agent derives `user_id` from participant identity or metadata
- Configures STT, TTS, and LLM services
- Sends greeting prompt and listens for workout commands

### 2. Workout Processing
When you say something like *"I did 3 sets of 10 reps bench press at 185 pounds"*:

1. **Parser**: Extracts structured data (exercise, sets, reps, weight)
2. **Intent Router**: Determines action based on keywords and context
3. **Validator**: Checks for required fields (exercise, sets, reps, weight)
4. **Saver**: Writes to Supabase if validation passes

### 3. Intent Detection
- **"Show me my workouts from last week"** → Reader
- **"Delete my last workout"** → Deletor
- **"I did bench press"** (new) → Validator → Saver
- **"Update that to 200 pounds"** (with workout_id) → Updator

## Setup

### Prerequisites
- Python 3.10+
- Supabase account
- LiveKit server
- OpenAI API key
- Groq API key

### Environment Variables
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd gymmando-backend

# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn gymmando_api.main:app --reload

# Run the LiveKit agent
python gymmando_graph/livekit_agent.py
```

## Database Schema

### workouts table
- `id`: UUID (primary key)
- `user_id`: String (required)
- `exercise`: String (required)
- `sets`: Integer (required)
- `reps`: Integer (required)
- `weight`: Float (required)
- `rest_time`: Integer (optional)
- `comments`: String (optional)
- `created_at`: Timestamp
- `updated_at`: Timestamp

## Current Status

✅ **Working**
- Voice session handling
- Workout CRUD operations
- Natural language parsing
- Intent-based routing
- Data validation

🚧 **Stubbed/Planned**
- Authentication routes
- Health check endpoints
- Nutrition tracking module
- Body measurements module
- Additional LiveKit routes

## API Endpoints

### Current
- `POST /token` - Generate LiveKit access token

### Planned
- `/auth/*` - Authentication flows
- `/health` - Health checks
- `/livekit/*` - LiveKit management

## Development Notes

- All CRUD operations are scoped by `user_id`
- Missing `workout_id` for updates/deletes triggers auto-selection of most recent workout
- Validation errors return missing fields for follow-up prompts
- State flows through LangGraph nodes as `WorkoutState`

## Contributing

This is an early-stage MVP. The workout module is functional and serves as a template for nutrition and measurements modules.

## License

[Add your license here]