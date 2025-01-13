import os

from datetime import datetime, timezone
from typing import List, Tuple
from src import config
from src.csv_handler import CSVHandler
from src.db_handler import DBHandler
from src.utils.logger import Logging
from src.utils.error_handling import log_exceptions, TransactionProcessingError

"""
transaction_exporter.py


Classes:
    TransactionExporter: Handles fetching, processing, and exporting transaction data.

Functionality:
    - Connects to the database and retrieves transaction records.
    - Processes data (e.g., formatting dates, categorizing transactions).
    - Writes the processed transaction data to a CSV file.
"""

logger = logging.getLogger(__name__)


class TransactionExporter(Logging):
    """Handles the process of exporting transactions."""

    def __init__(self, db_file: str, output_csv: str):
        # Convert input paths to absolute paths using os.path.abspath
        self.db_file = os.path.abspath(db_file)
        self.output_csv = os.path.abspath(output_csv)
        self.existing_data: List[List[str]] = []  # Changed to List[List[str]]

    @log_exceptions(Logging.get_logger())
    def rename_existing_file(self) -> None:
        """Adds a '_old' suffix to the file if it already exists."""
        try:
            base, ext = os.path.splitext(self.output_csv)
            new_name = f"{base}_old{ext}"
            os.rename(self.output_csv, new_name)
            self.logger.info(f"Renamed existing file to {new_name}.")
        except FileNotFoundError:
            self.logger.debug(f"No file found to rename: {self.output_csv}")
        except Exception as e:
            self.logger.error(f"Error renaming file {self.output_csv}: {e}")
            raise TransactionProcessingError(f"Failed to rename file: {self.output_csv}")

    @log_exceptions(Logging.get_logger())
    def process_rows(self, rows: List[Tuple]) -> List[List[str]]:
        """Processes and maps database rows into a format suitable for export."""
        processed = []
        for row in rows:
            try:
                mapped_row = self.map_row(row)
                reordered_row = [mapped_row[col] for col in config.COLUMN_ORDER]
                processed.append(reordered_row)
            except (IndexError, KeyError, ValueError, TypeError) as e:
                # Emit full exception for debugging
                self.logger.warning(f"Skipping row {row}; Error: {e}")
                continue  # Ensure we skip to the next row on failure
            except Exception as e:
                print(f"Unhandled error processing row {row}: {e}")
                self.logger.error(f"Unhandled error processing row {row}: {e}")
                continue
        self.logger.info(f"Processed {len(processed)} rows successfully.")
        return processed

    def map_row(self, row: Tuple) -> dict:
        """Maps a database row (tuple) to a formatted list for CSV export."""
        return {
            'id': row[0],
            'opis': row[1],
            'kwota': self.format_amount(row[2]),
            'kategoria': self.map_category(row[3]),
            'data': self.format_timestamp(row[4]),
        }

    @staticmethod
    @log_exceptions(Logging.get_logger())
    def format_timestamp(unix_timestamp: int) -> str:
        """Formats the timestamp into a human-readable date with the timezone specified in config."""
        try:
            # Load timezone from config
            local_tz = timezone(config.TIMEZONE)
            # Convert to timezone-aware datetime
            localized_time = datetime.fromtimestamp(unix_timestamp, tz=utc).astimezone(local_tz)
            return localized_time.strftime("%d.%m.%Y")
        except (ValueError, TypeError) as e:
            CSVHandler.get_logger().error(f"Error formatting timestamp {unix_timestamp}: {e}")
            return str(unix_timestamp)

    @staticmethod
    @log_exceptions(Logging.get_logger())
    def format_amount(amount: float) -> str:
        """Formats the amount with a comma as the decimal separator."""
        try:
            return "{:,.2f}".format(float(amount)).replace('.', ',')
        except (ValueError, TypeError) as e:
            CSVHandler.get_logger().error(f"Error formatting amount {amount}: {e}")
            raise

    @staticmethod
    @log_exceptions(Logging.get_logger())
    def map_category(category_fk: str) -> str:
        """Maps a `category_fk` to a category or warns if it is unrecognized."""
        mapped_category = config.CATEGORY_MAPPING.get(str(category_fk), 'inne')
        if mapped_category == 'inne':
            CSVHandler.get_logger().warning(
                f"Unrecognized category_fk: {category_fk}. Defaulting to 'inne'."
            )
        return mapped_category

    @log_exceptions(Logging.get_logger())
    def fetch_and_export(self) -> None:
        """Fetches rows from DB, processes them, and writes them to a CSV."""
        history_file = self.output_csv
        history_backup_file = f"{os.path.splitext(self.output_csv)[0]}_previous{os.path.splitext(self.output_csv)[1]}"
        new_records_file = f"{os.path.splitext(self.output_csv)[0]}_new{os.path.splitext(self.output_csv)[1]}"

        # Backup the existing history file if it exists
        if os.path.exists(history_file):
            if os.path.exists(history_backup_file):
                os.remove(history_backup_file)
            os.rename(history_file, history_backup_file)

        # Fetch rows
        transactions = DBHandler.fetch_transactions(self.db_file, config.DATE_FILTER)

        # Process rows
        processed_data = self.process_rows(transactions)
        self.existing_data = CSVHandler.read_existing_csv(history_file)  # Already returns List[List[str]]

        # Filter for only new rows
        new_data = [row for row in processed_data if row not in self.existing_data]

        # Export only the new records to the new records file
        CSVHandler.write_to_csv(new_records_file, config.COLUMN_ORDER, new_data)

        if not new_data:
            self.logger.info("No new transactions to export.")
        else:
            # Merge new data into the history file
            updated_history_data = self.existing_data + new_data
            CSVHandler.write_to_csv(history_file, config.COLUMN_ORDER, updated_history_data)
            self.logger.info(f"Exported {len(new_data)} new transactions to '{new_records_file}'.")
