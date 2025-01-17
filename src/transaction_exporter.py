import os
from datetime import datetime
from typing import List, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import config
from src.csv_handler import CSVHandler
from src.db_handler import DBHandler
from src.utils.error_handling import log_exceptions
from src.utils.logger import Logging

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
        # Define file paths
        transactions_file = os.path.join(self.output_dir, f"{config.NEW_TRANSACTION_FILE}")
        history_file = os.path.join(self.output_dir, f"{config.TRANSACTION_HISTORY_FILE}")
        history_backup_file = os.path.join(self.output_dir, f"{config.PREVIOUS_TRANSACTION_HISTORY_FILE}")

        # Fetch rows from the database
        transactions = DBHandler.fetch_transactions(self.db_file, config.DATE_FILTER)

        # Process rows
        processed_data = self.process_rows(transactions)

        # Check existing history file
        if os.path.exists(history_file):
            existing_data = CSVHandler.read_existing_csv(history_file)
        else:
            existing_data = []

        # Identify new transactions
        new_transactions = [row for row in processed_data if row not in existing_data]

        if not new_transactions:
            self.logger.info("No new transactions to process. Skipping file generation.")
            return  # Stop further processing if no new data

        # Backup the existing history file as history_previous
        if os.path.exists(history_file):
            if os.path.exists(history_backup_file):
                os.remove(history_backup_file)
            os.rename(history_file, history_backup_file)
            self.logger.info(f"Moved '{history_file}' to '{history_backup_file}'.")

        # Export new transactions to transactions.csv
        CSVHandler.write_to_csv(transactions_file, config.COLUMN_ORDER, new_transactions)
        self.logger.info(f"Exported all transactions to '{transactions_file}'.")

        # Append new transactions to history
        updated_history_data = existing_data + new_transactions
        CSVHandler.write_to_csv(history_file, config.COLUMN_ORDER, updated_history_data)
        self.logger.info(f"Appended {len(new_transactions)} new transactions to '{history_file}'.")

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
                self.logger.warning(f"Skipping row {row} due to error: {e}")
                continue
        self.logger.info(f"Processed {len(processed)} rows successfully.")
        return processed

    def map_row(self, row: Tuple) -> dict:
        """Maps a database row (tuple) to a dictionary for CSV export."""
        return {
            'id': row[0],
            'opis': row[1],
            'kwota': self.format_amount(row[2]),
            'kategoria': self.map_category(row[3]),
            'data': self.format_timestamp(row[4]),
        }

    @staticmethod
    def format_timestamp(unix_timestamp: int) -> str:
        """Formats the UNIX timestamp into a human-readable date using the configured timezone."""
        try:
            local_tz = ZoneInfo(config.TIMEZONE)

            # Convert the timestamp to localized time
            localized_time = datetime.fromtimestamp(unix_timestamp, tz=local_tz)
            return localized_time.strftime("%Y-%m-%d")
        except (ZoneInfoNotFoundError, ValueError, TypeError) as e:
            # Handle errors and provide fallback
            Logging.get_logger().error(
                f"Error formatting timestamp {unix_timestamp} with timezone '{config.TIMEZONE}': {e}"
            )
            return str(unix_timestamp)

    @staticmethod
    def format_amount(amount: float) -> str:
        """Formats the amount with a comma as the decimal separator."""
        return "{:,.2f}".format(float(amount)).replace('.', ',')

    @staticmethod
    def map_category(category_name: str) -> str:
        """Maps category foreign keys to their corresponding names."""
        cat: str = category_name.lower()
        return cat if cat in config.CATEGORIES else 'inne'
