import os
from typing import cast

from dotenv import load_dotenv
from fastapi import FastAPI
from livekit import api

load_dotenv()

app = FastAPI()


def create_livekit_token(identity: str = "user_123", room: str = "gym-room") -> str:
    """Create a LiveKit access token for the given identity and room."""
    token = api.AccessToken(
        api_key=os.getenv("LIVEKIT_API_KEY"), api_secret=os.getenv("LIVEKIT_API_SECRET")
    )

    token.with_identity(identity)
    token.with_name("Gym User")
    token.with_grants(api.VideoGrants(room_join=True, room=room))

    return cast(str, token.to_jwt())


@app.get("/token")
def get_token():
    """Generate a LiveKit token for client connection."""
    token = create_livekit_token()
    return {"token": token}
