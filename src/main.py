import os
import sys

from src.transaction_exporter import TransactionExporter
from src.utils.logger import setup_logger

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
