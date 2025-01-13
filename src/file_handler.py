import csv

"""
file_handler.py

This module provides utilities for managing file operations, 
specifically writing data to CSV files.
"""


class FileHandler:
    """Handles file operations, such as writing data to CSV files."""

    @staticmethod
    def write_to_file(file_path, rows):
        """
        Write rows of data to a CSV file.

        :param file_path: Path to the output CSV file.
        :param rows: List of rows to be written, where each row is a list or tuple.
        """
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerows(rows)
        except Exception as e:
            raise IOError(f"Failed to write to file {file_path}: {e}")
