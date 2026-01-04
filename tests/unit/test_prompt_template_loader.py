"""Unit tests for PromptTemplateLoader class."""

from pathlib import Path
from unittest.mock import patch

import pytest

from gymmando_graph.utils.prompt_template_loader import PromptTemplateLoader


class TestPromptTemplateLoader:
    """Test suite for PromptTemplateLoader class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_with_templates_directory(self):
            templates_dir = "/path/to/templates"
            loader = PromptTemplateLoader(templates_dir)

            assert loader.templates_directory == Path(templates_dir)
            assert isinstance(loader.templates_directory, Path)

    class TestLoadTemplate:
        """Test load_template method."""

        def test_load_template_reads_file(self):
            templates_dir = "/tmp/test_templates"
            loader = PromptTemplateLoader(templates_dir)
            template_content = "This is a test template"

            with patch("pathlib.Path.read_text", return_value=template_content):
                result = loader.load_template("test_template.md")

                assert result == template_content

        def test_load_template_raises_file_not_found_error(self):
            templates_dir = "/tmp/test_templates"
            loader = PromptTemplateLoader(templates_dir)

            with patch("pathlib.Path.read_text", side_effect=FileNotFoundError()):
                with pytest.raises(FileNotFoundError):
                    loader.load_template("nonexistent.md")

        def test_load_template_raises_permission_error(self):
            templates_dir = "/tmp/test_templates"
            loader = PromptTemplateLoader(templates_dir)

            with patch("pathlib.Path.read_text", side_effect=PermissionError()):
                with pytest.raises(PermissionError):
                    loader.load_template("protected.md")

        def test_load_template_uses_utf8_encoding(self):
            templates_dir = "/tmp/test_templates"
            loader = PromptTemplateLoader(templates_dir)
            template_content = "Test content with unicode: 测试"

            with patch(
                "pathlib.Path.read_text", return_value=template_content
            ) as mock_read:
                result = loader.load_template("test.md")
                mock_read.assert_called_once_with(encoding="utf-8")
                assert result == template_content
