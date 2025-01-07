import logging

LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_DATEFMT = '%H:%M:%S'


def setup_logger(class_name: str) -> logging.Logger:
    """Set up a logger for a specific class."""
    logging.basicConfig(
        level=LOGGING_LEVEL,
        format=LOGGING_FORMAT,
        datefmt=LOGGING_DATEFMT,
        force=True,  # Ensures no existing logging handlers interfere
    )
    return logging.getLogger(class_name)


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
