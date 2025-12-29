"""Database module for Supabase integration."""

# Remove 'supabase' from this import line
from gymmando_graph.database.client import get_supabase_client

# Remove 'supabase' from the exported names list
__all__ = ["get_supabase_client"]
