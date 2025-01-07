import logging
import sys
import os
from src.transaction_exporter import TransactionExporter

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry-point script for data export."""
    if len(sys.argv) != 3:
        logger.error("Usage: python main.py <db_file> <output_csv>")
        sys.exit(1)

    db_file = sys.argv[1]
    output_csv = sys.argv[2]

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
