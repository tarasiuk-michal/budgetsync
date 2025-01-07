import logging
import os
from datetime import datetime
from typing import List, Tuple

from src import config
from src.csv_handler import CSVHandler
from src.db_handler import DBHandler

logger = logging.getLogger(__name__)


class TransactionExporter:
    """Handles the entire process of exporting transactions."""

    def __init__(self, db_file: str, output_csv: str):
        self.db_file = db_file
        self.output_csv = output_csv
        self.existing_data = set()

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

    def format_timestamp(self, unix_timestamp: int) -> str:
        """Formats the timestamp into a human-readable date."""
        try:
            return datetime.utcfromtimestamp(unix_timestamp).strftime("%d.%m.%Y")
        except (ValueError, TypeError) as e:
            logger.error(f"[{TransactionExporter.__name__}] Error formatting timestamp {unix_timestamp}: {e}")
            return str(unix_timestamp)

    def format_amount(self, amount: float) -> str:
        """Formats the amount with a comma as the decimal separator."""
        try:
            return "{:,.2f}".format(float(amount)).replace('.', ',')
        except (ValueError, TypeError) as e:
            logger.error(f"[{TransactionExporter.__name__}] Error formatting amount {amount}: {e}")
            return str(amount)

    def map_category(self, category_fk: str) -> str:
        """Maps category_fk values to descriptive categories."""
        mapped_category = config.CATEGORY_MAPPING.get(str(category_fk), 'inne')
        if mapped_category == 'inne':
            logger.warning(
                f"[{TransactionExporter.__name__}] Unrecognized category_fk: {category_fk}. Defaulting to 'inne'.")
        return mapped_category

    def fetch_and_export(self) -> None:
        """Fetches data from the database, processes it, and exports it to CSV."""
        if os.path.exists(self.output_csv):
            self.rename_existing_file()

        # Fetch transactions
        transactions = DBHandler.fetch_transactions(self.db_file, config.DATE_FILTER)

        # Process the rows
        processed_data = self.process_rows(transactions)

        # Read existing data from the CSV file to avoid duplication
        self.existing_data = CSVHandler.read_existing_csv(self.output_csv)

        # Filter out already existing rows
        new_data = [row for row in processed_data if tuple(row) not in self.existing_data]

        if not new_data:
            logger.info(f"[{TransactionExporter.__name__}] No new transactions to export.")
        else:
            CSVHandler.write_to_csv(self.output_csv, config.COLUMN_ORDER, new_data)
            logger.info(
                f"[{TransactionExporter.__name__}] Exported {len(new_data)} new transactions to '{self.output_csv}'.")
