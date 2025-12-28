"""Database module for Supabase integration."""

from gymmando_graph.database.client import get_supabase_client, supabase

__all__ = ["supabase", "get_supabase_client"]
