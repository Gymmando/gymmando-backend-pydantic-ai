"""Base CRUD operations for all modules."""
from typing import Generic, Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseCRUD(Generic[T]):
    """Base CRUD with create, read, update, delete operations."""

    def __init__(self, table_name: str, model_class: Type[T]):
        self.table_name = table_name
        self.model_class = model_class

    def _get_client(self):
        """Lazy load Supabase client."""
        from gymmando_graph.database import get_supabase_client

        return get_supabase_client()

    def create(self, data: dict) -> Optional[T]:
        """Create a record."""
        client = self._get_client()
        response = client.table(self.table_name).insert(data).execute()
        return self.model_class(**response.data[0]) if response.data else None

    def read(self, id: str) -> Optional[T]:
        """Read a record by ID."""
        client = self._get_client()
        response = client.table(self.table_name).select("*").eq("id", id).execute()
        return self.model_class(**response.data[0]) if response.data else None

    def update(self, id: str, data: dict) -> Optional[T]:
        """Update a record."""
        client = self._get_client()
        response = client.table(self.table_name).update(data).eq("id", id).execute()
        return self.model_class(**response.data[0]) if response.data else None

    def delete(self, id: str) -> bool:
        """Delete a record."""
        client = self._get_client()
        response = client.table(self.table_name).delete().eq("id", id).execute()
        return bool(response.data)
