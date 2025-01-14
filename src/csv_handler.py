import csv
import os
from typing import List
from typing import TextIO  # noqa: F401

from src.utils.error_handling import log_exceptions, CSVError
from src.utils.logger import Logging

"""
Module: csv_handler

This module provides functionality for handling CSV file operations, such as creating,
writing, and modifying CSV files. It is primarily used in the transaction export workflow
to manage the output file.

Functions:
    - write_csv: Writes data to a CSV file with specified headers and rows.
    - rename_file: Renames an existing CSV file, useful for handling already existing exports.
    - append_to_csv: Appends new rows to an existing CSV file without modifying its structure.

Usage:
    Use this module to perform CSV-related tasks in the data export pipeline. It ensures proper
    formatting and supports handling file overwrites or appending additional data.
"""


class CSVHandler(Logging):
    """Handles CSV operations."""

    @staticmethod
    @log_exceptions(Logging.get_logger())
    def read_existing_csv(file_path: str) -> List[List[str]]:
        """Reads rows from an existing CSV file and returns them as a list of lists."""
        logger = CSVHandler.get_logger()
        logger.debug(f"[{CSVHandler.__name__}] Entering read_existing_csv with file_path={file_path}")

        if not os.path.exists(file_path):
            logger.info(f"[{CSVHandler.__name__}] {file_path} does not exist. Returning empty list.")
            return []

        try:
            with open(os.path.abspath(file_path), encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                next(reader, None)  # Skip the header
                rows = [list(row) for row in reader]
                logger.debug(f"Read {len(rows)} rows from {file_path}")
                return rows
        except FileNotFoundError:
            logger.warning(f"File {os.path.abspath(file_path)} not found. Returning empty list.")
            return []
        except Exception as e:
            logger.error(f"Error reading CSV at {os.path.abspath(file_path)}: {e}")
            raise CSVError(f"Failed to read CSV file: {file_path}")

    @staticmethod
    @log_exceptions(Logging.get_logger())
    def write_to_csv(file_path: str, headers: List[str], rows: List[List[str]]) -> None:

        """Writes rows to a CSV file with the specified headers."""
        logger = CSVHandler.get_logger()
        try:
            with open(os.path.abspath(file_path), 'w', encoding='utf-8', newline="") as file:  # type: TextIO
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(headers)  # Write headers
                writer.writerows(rows)
                logger.info(f"Wrote {len(rows)} rows to {os.path.abspath(file_path)}")
        except Exception as e:
            logger.error(f"Error writing to CSV at {os.path.abspath(file_path)}: {e}")
            raise CSVError(f"Failed to write to CSV file: {file_path}")
