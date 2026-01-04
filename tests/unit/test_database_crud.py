"""Unit tests for BaseCRUD class."""


from pydantic import BaseModel

from gymmando_graph.database.crud import BaseCRUD


class TestBaseCRUD:
    """Test suite for BaseCRUD class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_with_table_name_and_model_class(self):
            class TestModel(BaseModel):
                id: str
                name: str

            crud = BaseCRUD("test_table", TestModel)

            assert crud.table_name == "test_table"
            assert crud.model_class == TestModel
