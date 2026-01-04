"""Unit tests for Logger utility class."""

import logging
from pathlib import Path

from gymmando_graph.utils.logger import Logger


class TestLogger:
    """Test suite for Logger class."""

    class TestInit:
        """Test initialization methods."""

        def test_init_with_defaults(self):
            logger = Logger()

            assert logger.log_file is not None
            assert isinstance(logger.log_file, Path)
            assert logger.log_file.name == "app.log"
            assert logger.logger is not None
            assert isinstance(logger.logger, logging.Logger)
            assert logger.logger.name == "chat_app"

        def test_init_with_custom_name(self):
            custom_name = "test_logger"
            logger = Logger(name=custom_name)

            assert logger.logger is not None
            assert isinstance(logger.logger, logging.Logger)
            assert logger.logger.name == custom_name

        def test_init_with_custom_log_file(self):
            custom_log_file = Path("/tmp/test_custom.log")
            logger = Logger(log_file=custom_log_file)

            assert logger.log_file == custom_log_file
            assert isinstance(logger.log_file, Path)

    class TestGetLogger:
        """Test get_logger method."""

        def test_get_logger_returns_logger_instance(self):
            logger = Logger()
            logger_instance = logger.get_logger()

            assert isinstance(logger_instance, logging.Logger)
            assert logger_instance.name == "chat_app"

    class TestHandlers:
        """Test handler configuration."""

        def test_logger_has_file_and_stream_handlers(self):
            """Test that logging is configured with FileHandler and StreamHandler on root logger."""
            # Note: basicConfig only works once, so handlers may already be set from previous tests
            # We check the root logger since basicConfig sets handlers there
            Logger()
            root_handlers = logging.root.handlers

            assert (
                len(root_handlers) >= 2
            ), f"Expected at least 2 handlers on root logger, got {len(root_handlers)}"

            has_file_handler = any(
                isinstance(h, logging.FileHandler) for h in root_handlers
            )
            has_stream_handler = any(
                isinstance(h, logging.StreamHandler) for h in root_handlers
            )

            assert has_file_handler, "Root logger should have FileHandler"
            assert has_stream_handler, "Root logger should have StreamHandler"
