import os
import sys

from src.transaction_exporter import TransactionExporter
from src.utils.logger import setup_logger

"""
main.py

This script serves as the main entry point for exporting transaction data from the database to a CSV file.

Usage:
    python main.py <db_file> <output_csv>

Arguments:
    db_file: Path to the SQLite database file.
    output_csv: Path to the output CSV file.

Functionality:
    - Validates command-line arguments.
    - Ensures the database file exists.
    - Exports transactions from the database to the specified CSV file using the TransactionExporter class.
"""

logger = setup_logger(__name__)


def main() -> None:
    """Main entry-point script for data export."""
    if len(sys.argv) != 3:
        logger.error("Usage: python main.py <db_file> <output_csv>")
        sys.exit(1)

    db_file = os.path.abspath(sys.argv[1])  # Convert to absolute path
    output_csv = os.path.abspath(sys.argv[2])  # Convert to absolute path

    if not os.path.exists(db_file):
        logger.error(f"Database file '{db_file}' does not exist.")
        sys.exit(1)

    try:
        exporter = TransactionExporter(db_file, output_csv)
        exporter.fetch_and_export()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
