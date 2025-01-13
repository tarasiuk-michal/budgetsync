import os
import sys

from config import DB_FILE_PREFIX, DB_FILE_SUFFIX
from src.file_handler import FileHandler
from src.transaction_exporter import TransactionExporter
from src.utils.logger import setup_logger

"""
main.py

Exports transaction data from the database to CSV files.

Features:
- Identifies the latest SQL database file with a defined prefix in the specified directory.
- Generates the following files:
    - `transactions.csv`: Stores new transactions.
    - `transactions_history_previous.csv`: Backs up the previous transaction history.
    - `transactions_history.csv`: Combines old and new transaction data.

Usage:
    python main.py [db_directory]

Arguments:
    db_directory: Path to the directory containing SQL database files (defaults to the current directory).
"""

logger = setup_logger(__name__)


def main() -> None:
    """
    Main script for locating the latest SQL database file and exporting transaction data to CSV files.
    """
    # Get database directory, default to the current directory if not provided
    db_directory = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
    logger.info(f"Looking for database files in: {db_directory}")

    try:
        # Locate the latest 'cashew' SQL file in the directory
        latest_sql_file = FileHandler.find_latest_sql_file(db_directory)
        logger.info(f"Located latest '{DB_FILE_PREFIX}' '{DB_FILE_SUFFIX}' file: {latest_sql_file}")

        # Output directory is the same as the database directory
        output_dir = db_directory

        # Initialize and execute transaction export
        exporter = TransactionExporter(latest_sql_file, output_dir)
        exporter.fetch_and_export()

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
