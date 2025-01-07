import logging
import sqlite3
from typing import List, Tuple

logger = logging.getLogger(__name__)


class DBHandler:
    """Handles interactions with the database."""

    @staticmethod
    def fetch_transactions(db_path: str, date_filter: str) -> List[Tuple]:
        """Fetch transactions after the given date from the database."""
        logger.debug(
            f"[{DBHandler.__name__}] Entering fetch_transactions with db_path={db_path} and date_filter={date_filter}")
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
            logger.debug(f"[{DBHandler.__name__}] Fetched {len(rows)} transactions.")
            return rows
        except sqlite3.OperationalError as e:
            logger.error(f"[{DBHandler.__name__}] Database operation failed: {e}")
            raise
        finally:
            conn.close()
            logger.debug(f"[{DBHandler.__name__}] Exiting fetch_transactions.")
