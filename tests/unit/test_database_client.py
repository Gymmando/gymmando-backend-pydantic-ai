"""Unit tests for Supabase database client."""

import os
from unittest.mock import patch

from gymmando_graph.database.client import get_supabase_client


class TestGetSupabaseClient:
    """Test suite for get_supabase_client function."""

    class TestInit:
        """Test client initialization."""

        def test_get_supabase_client_initializes_client(self):
            with patch.dict(
                os.environ,
                {
                    "SUPABASE_URL": "https://test.supabase.co",
                    "SUPABASE_KEY": "test_key",
                },
            ):
                with patch(
                    "gymmando_graph.database.client.create_client"
                ) as mock_create:
                    mock_client = mock_create.return_value
                    result = get_supabase_client()

                    assert result == mock_client
                    mock_create.assert_called_once_with(
                        "https://test.supabase.co", "test_key"
                    )
