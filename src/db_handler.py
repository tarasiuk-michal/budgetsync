import sqlite3
from pathlib import Path
from typing import List, Tuple
from src.utils.logger import Logging


class DBHandler(Logging):
    """Handles interactions with the database."""

    @staticmethod
    def fetch_transactions(db_path: Path, date_filter: str) -> List[Tuple]:
        """Fetch transactions after the given date from the database."""
        logger = DBHandler.get_logger()  # Static method access to logger
        logger.debug("Entering fetch_transactions with db_path={db_path} and date_filter={date_filter}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            query = """
                SELECT transaction_pk, name, amount, category_fk, date_created
                FROM transactions
                WHERE date_created > strftime('%s', ?)
            """
            cursor.execute(query, (date_filter,))
            rows = cursor.fetchall()
            logger.debug("Fetched {len(rows)} transactions.")
            return rows
        except sqlite3.OperationalError as e:
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            conn.close()
            logger.debug("Exiting fetch_transactions.")
