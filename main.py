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
    python main.py [db_directory] [output_directory]

Arguments:
    db_directory: Path to the directory containing SQL database files.
                  Defaults to ./db (if it exists) or ./ (current working directory).
    output_directory: Path where output files will be saved.
                      Defaults to ./output (if it exists) or ./ (current working directory).
"""

logger = setup_logger(__name__)

# Dynamically add the parent directory of 'src' to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current file's directory
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))  # Navigate one level up
work_dir = os.getcwd()
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def main() -> None:
    """
    Main script for locating the latest SQL database file and exporting transaction data to CSV files.
    """
    # Get database and output directories from FileHandler
    db_directory = FileHandler.get_db_directory(sys.argv)
    output_directory = FileHandler.get_output_directory(sys.argv)

    logger.info(f"Looking for database files in: {db_directory}")
    logger.info(f"Output files will be saved in: {output_directory}")

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    try:
        # Locate the latest 'cashew' SQL file in the directory
        latest_sql_file = FileHandler.find_latest_sql_file(db_directory)
        logger.info(f"Located latest '{DB_FILE_PREFIX}' '{DB_FILE_SUFFIX}' file: {latest_sql_file}")

        # Initialize and execute transaction export
        exporter = TransactionExporter(latest_sql_file, output_directory)
        exporter.fetch_and_export()

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
