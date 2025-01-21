import os
import sys
from datetime import datetime

from config import MY_SPREADSHEET_ID, DB_FILE_PREFIX, DB_FILE_SUFFIX
from src.handlers.file_handler import FileHandler
from src.handlers.google_sheets_handler import GoogleSheetsHandler
from src.transaction_entity import TransactionEntity
from src.transaction_exporter import TransactionExporter
from src.utils.enums import Categories
from src.utils.logger import setup_logger

"""
main.py

Exports transaction data from the database to CSV files or Google Sheets.

Features:
- Identifies the latest SQL database file with a defined prefix in the specified directory.
- Supports exporting to CSV files or appending data to a Google Sheets document.
- Generates the following files (for CSV export):
    - `transactions.csv`: Stores new transactions.
    - `transactions_history_previous.csv`: Backs up the previous transaction history.
    - `transactions_history.csv`: Combines old and new transaction data.

Usage:
    python main.py [db_directory] [output_directory]

Arguments:
    db_directory: Path to the directory containing SQL database files.
                  Defaults to ./db (if it exists) or ./ (current working directory).
    output_directory: Path where output files will be saved. Only applicable for CSV export.
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
    # add_custom()
    # fetch_and_export()
    fetch_and_append()


if __name__ == "__main__":
    main()


def add_custom():
    """
    Adds custom transactions to the Google Sheets using the GoogleSheetsHandler.

    :return: None
    """
    # Initialize the Google Sheets handler with the spreadsheet ID
    g_handler = GoogleSheetsHandler(MY_SPREADSHEET_ID)

    # Create transaction entities with sample data
    r1 = TransactionEntity('', 'wyrównanie', -7.5, Categories.PRZYJEMNOŚCI.value, datetime(2025, 1, 20), 'Michał')
    r2 = TransactionEntity('', 'wyrównanie', -7.5, Categories.PRZYJEMNOŚCI.value, datetime(2025, 1, 20), 'Daga')

    # Append the transactions to the Google Sheet
    g_handler.append_transactions([r1.to_list(), r2.to_list()])


def fetch_and_export():
    """
    Locates the latest SQL database file and exports transaction data to CSV files.

    Steps:
    1. Identify database and output directories using FileHandler.
    2. Ensure the output directory exists.
    3. Find the latest SQL database file in the specified directory.
    4. Initialize the TransactionExporter and export transaction data.
    """
    # Retrieve database and output directories from command-line arguments
    db_directory = FileHandler.get_db_directory(sys.argv)
    output_directory = FileHandler.get_output_directory(sys.argv)

    logger.info(f"Searching for database files in: {db_directory}")
    logger.info(f"Output files will be stored in: {output_directory}")

    # Create the output directory if it does not exist
    os.makedirs(output_directory, exist_ok=True)

    try:
        # Find the most recent SQL file matching the defined prefix and suffix
        latest_sql_file = FileHandler.find_latest_sql_file(db_directory)
        logger.info(
            f"Located latest database file with prefix '{DB_FILE_PREFIX}' and suffix '{DB_FILE_SUFFIX}': {latest_sql_file}")

        # Initialize the transaction exporter and perform data export
        exporter = TransactionExporter(latest_sql_file, output_directory)
        exporter.fetch_and_export()

    except FileNotFoundError as e:
        logger.error(f"Database file missing: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during export: {e}")
        sys.exit(1)


def fetch_and_append():
    """
    Locates the latest SQL database file and appends new transactions to Google Sheets.

    Steps:
    1. Identify the database directory using FileHandler.
    2. Locate the latest SQL database file matching the specified prefix and suffix.
    3. Initialize the Google Sheets handler and transaction exporter.
    4. Fetch and append new transactions to the Google Sheet.
    """
    # Retrieve the database directory from command-line arguments
    db_directory = FileHandler.get_db_directory(sys.argv)
    logger.info(f"Searching for database files in: {db_directory}")

    try:
        # Find the most recent SQL file in the specified directory
        latest_sql_file = FileHandler.find_latest_sql_file(db_directory)
        logger.info(
            f"Located the latest database file matching '{DB_FILE_PREFIX}' and '{DB_FILE_SUFFIX}': {latest_sql_file}")

        # Initialize the transaction exporter and Google Sheets handler
        exporter = TransactionExporter(latest_sql_file)
        g_handler = GoogleSheetsHandler(MY_SPREADSHEET_ID)

        # Fetch and append new transactions to Google Sheets
        exporter.fetch_and_append(latest_sql_file, g_handler)

    except FileNotFoundError as e:
        logger.error(f"Database file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during the process: {e}")
        sys.exit(1)
