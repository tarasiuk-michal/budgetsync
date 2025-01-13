import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from src import config
from src.csv_handler import CSVHandler
from src.db_handler import DBHandler
from src.utils.error_handling import log_exceptions, TransactionProcessingError
from src.utils.logger import Logging


class TransactionExporter(Logging):
    """Handles the process of exporting transactions."""

    def __init__(self, db_file: Path, output_csv: Path):
        self.db_file = db_file
        self.output_csv = output_csv
        self.existing_data: set[tuple[str, ...]] = set()

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
        """Converts a UNIX timestamp to a human-readable format."""
        try:
            return datetime.fromtimestamp(unix_timestamp, tz=datetime.timezone.utc).strftime("%d.%m.%Y")
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
        if os.path.exists(self.output_csv):
            self.rename_existing_file()

        # Fetch rows
        transactions = DBHandler.fetch_transactions(self.db_file, config.DATE_FILTER)

        # Process rows
        processed_data = self.process_rows(transactions)
        self.existing_data = CSVHandler.read_existing_csv(self.output_csv)

        # Filter for only new rows
        new_data = [row for row in processed_data if tuple(row) not in self.existing_data]

        if not new_data:
            self.logger.info("No new transactions to export.")
        else:
            CSVHandler.write_to_csv(self.output_csv, config.COLUMN_ORDER, new_data)
            self.logger.info(f"Exported {len(new_data)} new transactions to '{self.output_csv}'.")
