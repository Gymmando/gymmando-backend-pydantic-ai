"""
Supabase database client initialization.
"""

import os

from dotenv import load_dotenv
from supabase import Client, create_client

from gymmando_graph.utils import Logger

logger = Logger().get_logger()

load_dotenv()


def get_supabase_client() -> Client:
    """Get initialized Supabase client."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error(
            "Failed to initialize Supabase client: Missing SUPABASE_URL or SUPABASE_KEY environment variables"
        )
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

    try:
        client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise


supabase: Client = get_supabase_client()
