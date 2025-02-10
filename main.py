import os
import sys
from datetime import datetime

from config import MY_SPREADSHEET_ID, GSHEETS_AUTH_CREDENTIALS_FILE
from src.handlers.file_handler import FileHandler
from src.handlers.google_sheets_handler import GoogleSheetsHandler
from src.transaction_entity import TransactionEntity
from src.transaction_exporter import TransactionExporter
from src.utils.enums import Categories
from src.utils.logger import setup_logger

"""
main.py

Exports transaction data from the database to Google Sheets or CSV files.

Features:
- Identifies the latest SQL database file with a defined prefix in the specified directory.
- Supports appending new transaction data to a Google Sheets document.
- Optionally supports exporting data to CSV files (this feature is currently inactive).
- (Optional) Adds custom transactions to the Google Sheet (add_custom function is defined but not called).

Usage:
    python main.py [db_directory]

Arguments:
    db_directory: Path to the directory containing SQL database files.
                  Defaults to ./db (if it exists) or ./ (current working directory).

Optional Features:
    - `fetch_and_export()`: Exports data to CSV files (currently commented out).
    - `add_custom()`: Adds predefined transactions to the Google Sheets document (currently commented out).
"""

logger = setup_logger(__name__)

# Dynamically add the parent directory of 'src' to sys.path
logger.debug("Setting up dynamic sys.path for the parent directory of 'src'.")
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current file's directory
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))  # Navigate one level up
work_dir = os.getcwd()
auth_file = str(os.path.join(current_dir, GSHEETS_AUTH_CREDENTIALS_FILE))

logger.debug(f"Current dir: {current_dir}, Parent dir: {parent_dir}, Work dir: {work_dir}")

if parent_dir not in sys.path:
    logger.debug("Adding parent directory to sys.path.")
    sys.path.insert(0, parent_dir)


def add_custom():
    """
    Adds custom transactions to the Google Sheets using the GoogleSheetsHandler.

    :return: None
    """
    logger.debug("Entering add_custom() function.")

    logger.debug("Initializing GoogleSheetsHandler with MY_SPREADSHEET_ID.")
    g_handler = GoogleSheetsHandler(MY_SPREADSHEET_ID)

    logger.debug("Creating custom transaction entities (examples).")
    r1 = TransactionEntity('', 'wyrównanie', -7.5, Categories.PRZYJEMNOŚCI.value, datetime(2025, 1, 20), 'Michał')
    r2 = TransactionEntity('', 'wyrównanie', -7.5, Categories.PRZYJEMNOŚCI.value, datetime(2025, 1, 20), 'Daga')

    logger.debug("Appending the transaction entities to Google Sheets.")
    g_handler.append_transactions([r1.to_list(), r2.to_list()])
    logger.debug("Custom transactions successfully added to Google Sheets.")


def fetch_and_export():
    """
    Locates the latest SQL database file and exports transaction data to CSV files.

    Steps:
    1. Identify database and output directories using FileHandler.
    2. Ensure the output directory exists.
    3. Find the latest SQL database file in the specified directory.
    4. Initialize the TransactionExporter and export transaction data.
    """
    logger.debug("Entering fetch_and_export() function.")

    logger.debug("Retrieving database and output directory paths from command-line arguments.")
    db_directory = FileHandler.get_db_directory(sys.argv)
    output_directory = FileHandler.get_output_directory(sys.argv)

    logger.info(f"Searching for database files in: {db_directory}")
    logger.info(f"Output files will be stored in: {output_directory}")

    logger.debug("Creating the output directory if it does not exist.")
    os.makedirs(output_directory, exist_ok=True)

    try:
        logger.debug("Finding the most recent SQL file matching the defined prefix and suffix.")
        latest_sql_file = FileHandler.find_latest_sql_file(db_directory)
        logger.info(f"Located latest database file: {latest_sql_file}")

        logger.debug("Initializing TransactionExporter with the found database file.")
        exporter = TransactionExporter(latest_sql_file, output_directory)

        logger.debug("Calling fetch_and_export() method of TransactionExporter.")
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
    logger.debug("Entering fetch_and_append() function.")

    logger.debug("Retrieving database directory from command-line arguments.")
    db_directory = FileHandler.get_db_directory(sys.argv)
    logger.info(f"Searching for database files in: {db_directory}")

    try:
        logger.debug("Finding the most recent SQL file in the database directory.")
        latest_sql_file = FileHandler.find_latest_sql_file(db_directory)
        logger.info(f"Located latest database file: {latest_sql_file}")

        logger.debug(
            f"Initializing GoogleSheetsHandler with sheet ID: {MY_SPREADSHEET_ID} and credentials file: {auth_file}")
        g_handler = GoogleSheetsHandler(MY_SPREADSHEET_ID, credentials_file=auth_file)
        logger.info(
            f"GoogleSheetsHandler initialized for sheet ID: {MY_SPREADSHEET_ID} and credentials file: {auth_file}")

        logger.debug("Initializing TransactionExporter with the database file.")
        exporter = TransactionExporter(latest_sql_file)
        logger.info(f"TransactionExporter initialized for database file: {latest_sql_file}")

        logger.debug("Calling fetch_and_append() method of TransactionExporter to update Google Sheets.")
        exporter.fetch_and_append(latest_sql_file, g_handler)

        logger.info("New transactions successfully appended to Google Sheets.")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during the process: {e}")
        sys.exit(1)


def main() -> None:
    logger.debug("Entering main() function. Starting the main program flow.")

    # logger.debug("Calling add_custom() to add transactions to Google Sheets.")
    # add_custom()
    #
    # logger.debug("Preparing to call fetch_and_export() to handle CSV export.")
    # fetch_and_export()  # Uncomment if needed

    logger.debug("Preparing to call fetch_and_append() to handle appending data to Google Sheets.")
    fetch_and_append()


if __name__ == "__main__":
    logger.debug("Script execution started (__name__ == '__main__').")
    main()
