import logging
import os
from datetime import datetime
from typing import List, Tuple

from pytz import timezone, utc

from src import config
from src.csv_handler import CSVHandler
from src.db_handler import DBHandler

"""
transaction_exporter.py

This module handles exporting transaction data from a database to a CSV file,
performing necessary transformations and formatting during the process.
"""

logger = logging.getLogger(__name__)


class TransactionExporter:
    """Handles the process of exporting transactions."""

    def __init__(self, db_file: str, output_csv: str):
        self.db_file = db_file
        self.output_csv = output_csv
        self.existing_data: List[List[str]] = []  # Changed to List[List[str]]

    def rename_existing_file(self) -> None:
        """Renames the existing CSV file to add a '_old' suffix."""
        try:
            base, ext = os.path.splitext(self.output_csv)
            new_name = f"{base}_old{ext}"
            os.rename(self.output_csv, new_name)
            logger.info(f"[{TransactionExporter.__name__}] Renamed existing file to {new_name}.")
        except Exception as e:
            logger.error(f"[{TransactionExporter.__name__}] Error renaming file {self.output_csv}: {e}")

    def process_rows(self, rows: List[Tuple]) -> List[List[str]]:
        """Processes and maps fetched rows into the desired format."""
        processed = []
        for row in rows:
            try:
                mapped_row = {
                    'id': row[0],
                    'opis': row[1],
                    'kwota': self.format_amount(row[2]),
                    'kategoria': self.map_category(row[3]),
                    'data': self.format_timestamp(row[4]),
                }
                reordered_row = [mapped_row[col] for col in config.COLUMN_ORDER]
                processed.append(reordered_row)
            except IndexError as e:
                logger.warning(f"[{TransactionExporter.__name__}] Skipping row due to index error {row}: {e}")
            except Exception as e:
                logger.error(f"[{TransactionExporter.__name__}] Error processing row {row}: {e}")
        return processed

    @staticmethod
    def format_timestamp(unix_timestamp: int) -> str:
        """Formats the timestamp into a human-readable date with the timezone specified in config."""
        try:
            # Load timezone from config
            local_tz = timezone(config.TIMEZONE)
            # Convert to timezone-aware datetime
            localized_time = datetime.fromtimestamp(unix_timestamp, tz=utc).astimezone(local_tz)
            return localized_time.strftime("%d.%m.%Y")
        except (ValueError, TypeError) as e:
            logger.error(f"[{TransactionExporter.__name__}] Error formatting timestamp {unix_timestamp}: {e}")
            return str(unix_timestamp)

    @staticmethod
    def format_amount(amount: float) -> str:
        """Formats the amount with a comma as the decimal separator."""
        try:
            return "{:,.2f}".format(float(amount)).replace('.', ',')
        except (ValueError, TypeError) as e:
            logger.error(f"[{TransactionExporter.__name__}] Error formatting amount {amount}: {e}")
            return str(amount)

    @staticmethod
    def map_category(category_fk: str) -> str:
        """Maps category_fk values to descriptive categories."""
        mapped_category = config.CATEGORY_MAPPING.get(str(category_fk), 'inne')
        if mapped_category == 'inne':
            logger.warning(
                f"[{TransactionExporter.__name__}] Unrecognized category_fk: {category_fk}. Defaulting to 'inne'.")
        return mapped_category

    def fetch_and_export(self) -> None:
        """Fetches data from the database, processes it, and exports it to CSV."""
        history_file = self.output_csv
        history_backup_file = f"{os.path.splitext(self.output_csv)[0]}_previous{os.path.splitext(self.output_csv)[1]}"
        new_records_file = f"{os.path.splitext(self.output_csv)[0]}_new{os.path.splitext(self.output_csv)[1]}"

        # Backup the existing history file if it exists
        if os.path.exists(history_file):
            if os.path.exists(history_backup_file):
                os.remove(history_backup_file)
            os.rename(history_file, history_backup_file)

        # Fetch transactions
        transactions = DBHandler.fetch_transactions(self.db_file, config.DATE_FILTER)

        # Process the rows
        processed_data = self.process_rows(transactions)

        # Read existing data from the CSV file to avoid duplication
        self.existing_data = CSVHandler.read_existing_csv(history_file)  # Already returns List[List[str]]

        # Filter out already existing rows
        new_data = [row for row in processed_data if row not in self.existing_data]

        # Export only the new records to the new records file
        CSVHandler.write_to_csv(new_records_file, config.COLUMN_ORDER, new_data)

        if not new_data:
            logger.info(f"[{TransactionExporter.__name__}] No new transactions to export.")
        else:
            # Merge new data into the history file
            updated_history_data = self.existing_data + new_data
            CSVHandler.write_to_csv(history_file, config.COLUMN_ORDER, updated_history_data)
            logger.info(
                f"[{TransactionExporter.__name__}] Exported {len(new_data)} new transactions to '{new_records_file}'.")
