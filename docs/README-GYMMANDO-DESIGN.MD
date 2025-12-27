gymmando/
├── core/
│   ├── __init__.py
│   ├── state.py           # Base state classes
│   ├── config.py          # API keys, settings
│   └── utils.py           # Shared utilities
│
├── agents/
│   ├── __init__.py
│   └── router/
│       ├── __init__.py
│       ├── agent.py       # Router logic
│       └── prompts.py     # Router prompts
│
├── modules/
│   ├── __init__.py
│   │
│   ├── workout/
│   │   ├── __init__.py
│   │   ├── graph.py       # LangGraph definition
│   │   ├── state.py       # WorkoutState schema
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py
│   │   │   └── query.py
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   ├── logger_prompts.py
│   │   │   └── query_prompts.py
│   │   ├── database.py    # Supabase operations
│   │   └── utils.py       # Module-specific helpers
│   │
│   ├── nutrition/         # Future module
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   ├── state.py
│   │   └── ...
│   │
│   └── measurements/      # Future module
│       └── ...
│
├── database/
│   ├── __init__.py
│   ├── client.py          # Supabase client setup
│   └── models.py          # Shared DB models
│
├── api/
│   ├── __init__.py
│   ├── main.py            # FastAPI app
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── livekit.py
│   └── middleware.py
│
├── tests/
│   ├── unit/
│   │   ├── test_router.py
│   │   └── test_workout_logger.py
│   └── integration/
│       └── test_workout_flow.py
│
├── .env
├── requirements.txt
└── README.md