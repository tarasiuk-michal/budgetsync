import functools

"""
error_handling.py

This module provides custom error handling functionality for the application.

Classes:
    CustomError: Base class for custom application exceptions.
    DatabaseError: Exception for handling database-related errors.

Functionality:
    - Defines and raises custom exceptions for better error management.
"""


class CSVError(Exception):
    """Custom exception for CSV-related operations."""


class DatabaseError(Exception):
    """Custom exception for database-related operations."""


class TransactionProcessingError(Exception):
    """Custom exception for transaction processing issues."""


def log_exceptions(logger):
    """
    Decorator to log any exceptions raised in a function.
    Automatically re-raises the exception after logging.
    """

    def decorator(func):
        """A decorator function to add additional functionality to another function or method."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper function to handle exceptions."""
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                raise

        return wrapper

    return decorator
