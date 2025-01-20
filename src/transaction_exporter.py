import os
import shutil
from typing import List, Tuple

import config
from .handlers.csv_handler import CSVHandler
from .handlers.db_handler import DBHandler
from .utils.error_handling import log_exceptions
from .utils.fomatter import Formatter
from .utils.logger import Logging

"""
transaction_exporter.py

Classes:
    TransactionExporter: Handles fetching, processing, and exporting transaction data.

Functionality:
    - Connects to the database and retrieves transaction records.
    - Writes new transactions to `transactions.csv`.
    - Creates a backup of `transactions_history.csv` as `transactions_history_previous.csv`.
    - Appends new transactions to `transactions_history.csv`.
"""


class TransactionExporter(Logging):
    """Handles the process of exporting transactions."""

    def __init__(self, db_file: str, output_dir: str):
        self.db_file = os.path.abspath(db_file)
        self.output_dir = os.path.abspath(output_dir)

    @log_exceptions(Logging.get_logger())
    def fetch_and_export(self) -> None:
        """Fetches rows from the database, processes them, and writes them to three output CSV files only if there are new transactions."""
        file_paths = self.define_file_paths()
        transactions = DBHandler.fetch_transactions(self.db_file, config.DATE_FILTER)
        new_transactions = self.extract_new_transactions(file_paths['history_file'], transactions)
        if not new_transactions:
            self.logger.info("No new transactions to process. Skipping file generation.")
            return
        self.backup_history_file(file_paths['history_file'], file_paths['history_backup_file'])
        self.write_transactions(file_paths, new_transactions)

    def define_file_paths(self):
        """Defines file paths for transactions, history, and backup."""
        return {
            'transactions_file': os.path.join(self.output_dir, f"{config.NEW_TRANSACTION_FILE}"),
            'history_file': os.path.join(self.output_dir, f"{config.TRANSACTION_HISTORY_FILE}"),
            'history_backup_file': os.path.join(self.output_dir, f"{config.PREVIOUS_TRANSACTION_HISTORY_FILE}")
        }

    @staticmethod
    def extract_new_transactions(history_file: str, transactions: list[list[str]]) -> list[Tuple]:
        """Filters and identifies new transactions."""

        historic_data = CSVHandler.read_existing_csv(history_file) if os.path.exists(history_file) else []

        # Extract IDs from the historic data (assuming IDs are the first column).
        historic_ids = {row[0] for row in historic_data}  # Use set for faster lookups.

        # Filter new transactions based on their IDs. Assuming IDs are also in the first column of transactions.
        new_data = [tuple(row) for row in transactions if row[0] not in historic_ids]

        return new_data

    def backup_history_file(self, history_file, history_backup_file):
        """Backups the existing history file."""
        if os.path.exists(history_file):
            if os.path.exists(history_backup_file):
                os.remove(history_backup_file)
            # Copy the current history file to the backup file
            shutil.copy(history_file, history_backup_file)
            self.logger.info(f"Copied '{history_file}' as '{history_backup_file}'.")

    def write_transactions(self, file_paths: dict[str, str], new_transactions: list[Tuple]):
        """Writes transactions and updates files appropriately."""
        processed_new_transactions = self.process_rows(new_transactions)
        CSVHandler.rewrite_csv(file_paths['transactions_file'], config.COLUMN_ORDER, processed_new_transactions)
        self.logger.info(f"Exported all transactions to '{file_paths['transactions_file']}'.")

        CSVHandler.append_to_csv(file_paths['history_file'], config.COLUMN_ORDER, processed_new_transactions)
        self.logger.info(f"Appended {len(new_transactions)} new transactions to '{file_paths['history_file']}'.")

    @log_exceptions(Logging.get_logger())
    def process_rows(self, rows: List[Tuple]) -> List[List[str]]:
        """Processes and maps database rows into a CSV-compatible format."""
        processed = []
        for row in rows:
            try:
                mapped_row = self.map_row(row)
                reordered_row = [mapped_row[col] for col in config.COLUMN_ORDER]
                processed.append(reordered_row)
            except Exception as e:
                self.logger.debug(f"Skipping row {row} due to error: {e}")
                continue
        self.logger.info(f"Processed {len(processed)} rows successfully.")
        return processed

    @staticmethod
    def map_row(row: Tuple) -> dict:
        """Maps a database row (tuple) to a dictionary for CSV export."""
        try:
            formed = {
                'id': row[0],
                'opis': row[1],
                'kwota': Formatter.format_amount(row[2]),
                'kategoria': Formatter.map_category(row[3]),
                'data': Formatter.format_timestamp(row[4]),
            }
        except Exception as e:
            raise e

        return formed
