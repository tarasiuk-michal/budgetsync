import os
import sqlite3
from typing import List, Tuple

from src.utils.error_handling import log_exceptions, DatabaseError
from src.utils.logger import Logging

"""
db_handler.py

This module provides functionality for database interactions.
It includes methods to connect to an SQLite database and retrieve transaction data based on specific criteria.

Classes:
    DBHandler: Provides an interface for performing database queries.

Exceptions:
    DatabaseError: Raised when a database operation encounters an error.
"""

GET_TRANSACTIONS_QUERY = """
                SELECT t.transaction_pk, t.name, t.amount, c.name AS category_name, t.date_created
                FROM transactions t
                JOIN categories c ON t.category_fk = c.category_pk
                WHERE t.date_created > strftime('%s', ?)
            """


class DBHandler(Logging):
    """
    Handles database interactions for querying and retrieving data.

    The DBHandler class provides methods to fetch transaction data from an SQLite
    database, while ensuring proper error handling and logging during database operations.
    """

    @staticmethod
    @log_exceptions(Logging.get_logger())
    def fetch_transactions(db_path: str, date_filter: str) -> List[Tuple]:
        """
        Fetch transactions from the database that occur after a specified date.

        :param db_path: A string representing the absolute path to the SQLite database file.
        :param date_filter: A string representing the date filter in 'YYYY-MM-DD' format.
        :return: A list of tuples, each representing a transaction's details.
        :raises DatabaseError: If an operational error occurs during the database query.
        """
        conn = None  # Initialize conn to None to ensure it is always defined
        db_path = os.path.abspath(db_path)  # Convert the path to an absolute path
        logger = DBHandler.get_logger()
        logger.debug(f"Connecting to DB at {db_path}")
        try:
            conn = sqlite3.connect(db_path)  # Try to create the database connection
            cursor = conn.cursor()
            cursor.execute(GET_TRANSACTIONS_QUERY, (date_filter,))
            rows = cursor.fetchall()
            logger.info(f"Fetched {len(rows)} transactions.")
            return rows
        except sqlite3.OperationalError as e:
            logger.error(f"Database operation failed: {e}")
            raise DatabaseError(f"Failed to fetch transactions: {e}")
        finally:
            if conn:  # Ensure conn is only closed if it was successfully initialized
                conn.close()
                logger.debug("Database connection closed.")
