import csv
import os
import re
from _typeshed import SupportsWrite
from datetime import datetime
from typing import Optional

from config import DB_FILE_PREFIX, DB_FILE_SUFFIX


class FileHandler:
    """
    Provides utilities for handling file operations, such as reading from
    or writing to files and locating specific files based on patterns.
    """

    @staticmethod
    def write_to_file(file_path, rows):
        """
        Writes a list of rows to a CSV file.

        :param file_path: Absolute or relative path to the CSV file.
        :param rows: A list of rows, where each row is represented as a list or tuple.
        :raises IOError: If an error occurs while writing to the file.
        """
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:  # type: SupportsWrite[str]
                writer = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerows(rows)
        except Exception as e:
            raise IOError(f"Failed to write to file {file_path}: {e}")

    @staticmethod
    def find_latest_sql_file(directory: str) -> str:
        """
        Locates the most recent SQL file in a directory based on its file name pattern.

        File names starting with a specific prefix and including a timestamp (YYYY-MM-DD-HH-MM-SS-FFFFFF)
        are considered. The timestamp determines the latest file.

        :param directory: Directory to search for files.
        :return: The absolute path to the SQL file with the most recent timestamp.
        :raises FileNotFoundError: If no matching file is found.
        """
        cashew_files = []
        # Regex pattern to allow optional characters between 'cashew-' and the timestamp, as well as after the timestamp
        cashew_pattern = re.compile(
            rf"'{DB_FILE_PREFIX}'.*?-(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{3}).*?\.'{DB_FILE_SUFFIX}'$")

        # Traverse through the directory
        for root, _, files in os.walk(directory):
            for file in files:
                if cashew_pattern.match(file):
                    cashew_files.append(os.path.join(root, file))

        if not cashew_files:
            raise FileNotFoundError("No matching 'cashew' .sql files found in the specified directory.")

        # Extract timestamps and sort files by datetime
        def extract_timestamp(file_name: str) -> Optional[datetime]:
            """
            Helper function to extract and parse the timestamp from the file name.

            :param file_name: Name of the file to extract the timestamp.
            :return: Parsed datetime object if the timestamp is valid, or None.
            """
            match = cashew_pattern.search(file_name)
            if match:
                # Extract timestamp group captured by the regex
                return datetime.strptime(match.group(1), "%Y-%m-%d-%H-%M-%S-%f")
            return None

        try:
            latest_file = max(
                cashew_files,
                key=lambda f: extract_timestamp(f) or datetime.min  # Use `datetime.min` for invalid cases
            )
            return os.path.abspath(latest_file)
        except ValueError:
            raise FileNotFoundError(f"No valid timestamp found in the {DB_FILE_PREFIX} {DB_FILE_SUFFIX} file names.")
