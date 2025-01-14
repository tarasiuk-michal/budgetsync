import csv
import os
import re
from datetime import datetime
from typing import Optional
from typing import TextIO  # noqa: F401


class FileHandler:
    """
    Provides utilities for handling file operations, such as reading from
    or writing to files and locating specific files based on patterns.
    """

    @staticmethod
    def write_to_file(file_path: str, rows: list[list[str]]) -> None:
        """
        Writes a list of rows to a CSV file.

        :param file_path: Absolute or relative path to the CSV file.
        :param rows: A list of rows, where each row is represented as a list or tuple.
        :raises IOError: If an error occurs while writing to the file.
        """
        try:
            # Use TextIO as the type for a file object when using context managers
            with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:  # type: TextIO
                writer = csv.writer(csv_file, delimiter=";", quoting=csv.QUOTE_MINIMAL)
                writer.writerows(rows)
        except Exception as e:
            raise IOError(f"Failed to write to file {file_path}: {e}")

    @staticmethod
    def find_latest_sql_file(directory: str) -> str:
        """
        Locates the most recent SQL file in a directory based on its file name pattern (directly in the directory, not recursively).

        :param directory: Directory to search for files.
        :return: The absolute path to the SQL file with the most recent timestamp.
        :raises FileNotFoundError: If no matching file is found.
        """
        import config  # Import config dynamically if not already imported

        # Compile the SQL_FILE_REGEX from config.py
        sql_file_name_pattern = re.compile(config.SQL_FILE_NAME_REGEX)

        try:
            # Get all files in the provided directory (non-recursive)
            files_in_directory = [
                os.path.join(directory, f) for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) and sql_file_name_pattern.match(f)
            ]
            print("files_in_directory: ", files_in_directory)
        except OSError as e:
            raise FileNotFoundError(f"Error accessing directory '{directory}': {e}")

        if not files_in_directory:
            raise FileNotFoundError(
                f"No matching '{config.DB_FILE_PREFIX}' {config.DB_FILE_SUFFIX} files found in {directory}")

        # Extract timestamps and sort files by datetime
        def extract_timestamp(file_name: str) -> Optional[datetime]:
            """
            Helper function to extract and parse the timestamp from the file name.

            :param file_name: Name of the file to extract the timestamp.
            :return: Parsed datetime object if the timestamp is valid, or None.
            """
            sql_file_datetime_pattern = re.compile(config.SQL_FILE_DATETIME_REGEX)
            match = sql_file_datetime_pattern.search(file_name)
            if match:
                try:
                    # Extract timestamp group captured by the regex
                    return datetime.strptime(match.group(), config.SQL_FILE_DATETIME_FORMAT)
                except ValueError:
                    return None
            return None

        try:
            latest_file = max(
                files_in_directory,
                key=lambda f: extract_timestamp(f) or datetime.min  # Use `datetime.min` for invalid cases
            )
            return os.path.abspath(latest_file)
        except ValueError:
            raise FileNotFoundError(
                f"No valid timestamp found in the {config.DB_FILE_PREFIX} {config.DB_FILE_SUFFIX} file names in {directory}."
            )

    @staticmethod
    def get_db_directory(cli_args) -> str:
        """
        Determines the database directory.

        :param cli_args: The list of command-line arguments.
        :return: The path to the database directory.
        """
        # If the first CLI argument is provided, use it as the db_directory
        if len(cli_args) > 1:
            return os.path.abspath(cli_args[1])
        else:
            # Default: Look for ./db if it exists in working directory or fallback to ./
            working_dir = os.getcwd()
            db_dir = os.path.join(working_dir, "db")
            return db_dir if os.path.exists(db_dir) else working_dir

    @staticmethod
    def get_output_directory(cli_args) -> str:
        """
        Determines the output directory.

        :param cli_args: The list of command-line arguments.
        :return: The path to the output directory.
        """
        # If the second CLI argument is provided, use it as the output_directory
        if len(cli_args) > 2:
            return os.path.abspath(cli_args[2])
        else:
            working_dir = os.getcwd()
            # Default: Save files in ./output if it exists in working directory or fallback to ./
            output_dir = os.path.join(working_dir, "output")
            return output_dir if os.path.exists(output_dir) else working_dir
