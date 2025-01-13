import csv
from pathlib import Path
from typing import List, Set, Tuple

from src.utils.error_handling import log_exceptions, CSVError
from src.utils.logger import Logging


class CSVHandler(Logging):
    """Handles CSV operations."""

    @staticmethod
    @log_exceptions(Logging.get_logger())
    def read_existing_csv(file_path: Path) -> Set[Tuple[str, ...]]:
        """Reads rows from an existing CSV file as a set of tuples."""
        logger = CSVHandler.get_logger()
        print(logger.propagate)  # Should return True
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                next(reader, None)  # Skip the header
                rows = {tuple(row) for row in reader}
                logger.debug(f"Read {len(rows)} rows from {file_path}")
                return rows
        except FileNotFoundError:
            logger.warning(f"File {file_path} not found. Returning empty set.")
            return set()
        except Exception as e:
            logger.error(f"Error reading CSV at {file_path}: {e}")
            raise CSVError(f"Failed to read CSV file: {file_path}")

    @staticmethod
    @log_exceptions(Logging.get_logger())
    def write_to_csv(file_path: Path, headers: List[str], rows: List[List[str]]) -> None:
        """Writes rows to a CSV file with the specified headers."""
        logger = CSVHandler.get_logger()
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(headers)  # Write headers
                writer.writerows(rows)
                logger.info(f"Wrote {len(rows)} rows to {file_path}")
        except Exception as e:
            logger.error(f"Error writing to CSV at {file_path}: {e}")
            raise CSVError(f"Failed to write to CSV file: {file_path}")
