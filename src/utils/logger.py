import logging

from config import LOG_LEVEL

"""
logger.py

This module handles logging functionality for the application.

Functionality:
    - Configures loggers for different levels (info, debug, error, etc.).
    - Writes log messages to console or log files.
"""

LOGGING_LEVEL = LOG_LEVEL
LOGGING_FORMAT = '%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s'
LOGGING_DATE_FORMAT = '%H:%M:%S'


def setup_logger(class_name: str) -> logging.Logger:
    """Set up and return a logger for a specific class with a StreamHandler."""
    logger = logging.getLogger(class_name)

    # If no handlers are attached, configure the logger (prevent duplicates)
    if not logger.hasHandlers():
        # Create a stream handler
        stream_handler = logging.StreamHandler()

        # Set the log format and level
        formatter = logging.Formatter(fmt=LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(LOGGING_LEVEL)

        # Add the handler to the logger
        logger.addHandler(stream_handler)

    # Set the logger's overall logging level and enable propagation
    logger.setLevel(LOGGING_LEVEL)
    logger.propagate = True

    return logger


class Logging:
    """Mixin to add a logger to a class."""

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Returns a logger specific to the calling class."""
        return setup_logger(cls.__name__)

    @property
    def logger(self) -> logging.Logger:
        """Instance-level access to the logger."""
        return self.get_logger()
