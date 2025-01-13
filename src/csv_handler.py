import csv
import logging
import os
from typing import List

logger = logging.getLogger(__name__)


class CSVHandler:
    """Handles reading and writing CSV files."""

    @staticmethod
    def read_existing_csv(file_path: str) -> List[List[str]]:
        """Reads existing rows from a CSV file into a list of lists of strings."""
        logger.debug(f"[{CSVHandler.__name__}] Entering read_existing_csv with file_path={file_path}")
        if not os.path.exists(file_path):
            logger.info(f"[{CSVHandler.__name__}] {file_path} does not exist. Returning empty data list.")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                data = [list(row) for row in reader]
                logger.debug(f"[{CSVHandler.__name__}] Read {len(data)} existing rows from CSV.")
                return data
        except Exception as e:
            logger.error(f"[{CSVHandler.__name__}] Error reading CSV file {file_path}: {e}")
            return []

    @staticmethod
    def write_to_csv(file_path: str, headers: List[str], rows: List[List[str]]) -> None:
        """Writes rows into a CSV file."""
        logger.debug(f"[{CSVHandler.__name__}] Entering write_to_csv with file_path={file_path}")
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(headers)
                writer.writerows(rows)
            logger.info(f"[{CSVHandler.__name__}] Successfully wrote {len(rows)} rows to {file_path}.")
        except Exception as e:
            logger.error(f"[{CSVHandler.__name__}] Error writing to CSV file {file_path}: {e}")
        logger.debug(f"[{CSVHandler.__name__}] Exiting write_to_csv.")
