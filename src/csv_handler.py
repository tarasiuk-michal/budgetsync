from typing import List, Set, Tuple
from pathlib import Path
from src.utils.logger import Logging


class CSVHandler(Logging):
    """Handles CSV operations."""

    @staticmethod
    def read_existing_csv(file_path: Path) -> Set[Tuple[str, ...]]:
        """Reads existing rows from a CSV file into a set of tuples."""
        logger = CSVHandler.get_logger()  # Static method access to logger
        logger.debug("Entering read_existing_csv with file_path={file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.read().strip().split("\n")
            rows = {tuple(line.split(";")) for line in lines[1:]}  # Skip header
        logger.debug("Fetched {len(rows)} rows from {file_path}")
        return rows

    @staticmethod
    def write_to_csv(file_path: Path, headers: List[str], rows: List[List[str]]) -> None:
        """Writes rows into a CSV file."""
        logger = CSVHandler.get_logger()  # Static method access to logger
        logger.debug("Entering write_to_csv with file_path={file_path}")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(";".join(headers) + "\n")
            for row in rows:
                for r in row:
                    if not r:
                        row[row.index(r)] = ""
                    else:
                        row[row.index(r)] = str(r)
                file.write(";".join(row) + "\n")
        logger.debug("Wrote {len(rows)} rows to {file_path}")
