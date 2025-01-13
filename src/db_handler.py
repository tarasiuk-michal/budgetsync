import os
import sqlite3
from typing import List, Tuple

from src.utils.error_handling import log_exceptions, DatabaseError
from src.utils.logger import Logging

"""
db_handler.py

This module provides functionality to interact with the database. 
It includes methods to connect to the database and fetch transaction data filtered by specific criteria.

Classes:
    DBHandler: Handles database operations like fetching transactions.

Exceptions:
    DatabaseError: Custom exception raised for database operation errors.
"""


class DBHandler(Logging):
    """Handles database interactions."""

    @staticmethod
    @log_exceptions(Logging.get_logger())
    def fetch_transactions(db_path: str, date_filter: str) -> List[Tuple]:
        """Fetches transactions from the database filtered by date."""
        conn = None  # Initialize conn to None to ensure it is always defined
        db_path = os.path.abspath(db_path)  # Convert the path to an absolute path
        logger = DBHandler.get_logger()
        logger.debug(f"Connecting to DB at {db_path}")
        try:
            conn = sqlite3.connect(db_path)  # Try to create the database connection
            cursor = conn.cursor()
            query = """
                SELECT transaction_pk, name, amount, category_fk, date_created
                FROM transactions
                WHERE date_created > strftime('%s', ?)
            """
            cursor.execute(query, (date_filter,))
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
