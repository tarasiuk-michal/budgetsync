import os
import sys
from pathlib import Path

from src.transaction_exporter import TransactionExporter
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


def main() -> None:
    """Main entry-point script for data export."""
    if len(sys.argv) != 3:
        logger.error("Usage: python main.py <db_file> <output_csv>")
        sys.exit(1)

    db_file = Path(sys.argv[1])
    output_csv = Path(sys.argv[2])

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
