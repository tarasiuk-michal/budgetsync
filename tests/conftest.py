import os
import sqlite3
import sys

import pytest

from src.handlers.google_sheets_handler import GoogleSheetsHandler
from src.transaction_exporter import TransactionExporter
from test_google_sheets_handler import SPREADSHEET_ID

TEST_ROWS = [(1, 'Groceries', 50.00, 'spożywcze', 1672531200), (2, 'Fuel', 30.00, 'transport', 1672617600)]
INVALID_TEST_ROWS = [(1, 'Groceries', 50.00, 'spożywcze', 1672531200), (4, 'Unknown', 25.00, '999', 1672790400)]
PATH_FETCH_TRANSACTIONS = 'src.handlers.db_handler.DBHandler.fetch_transactions'
PATH_READ_EXISTING_CSV = 'src.handlers.csv_handler.CSVHandler.read_existing_csv'
PATH_WRITE_TO_CSV = 'src.handlers.csv_handler.CSVHandler.write_to_csv'
PATH_WRITE_TO_FILE = 'src.handlers.file_handler.FileHandler.write_to_file'
PATH_MAP_ROW = 'src.transaction_exporter.TransactionExporter.map_row'
OS_RENAME = 'os.rename'
OS_REMOVE = 'os.remove'
OS_PATH_EXISTS = 'os.path.exists'

INSERT_TEST_TRANSACTIONS = """
        INSERT INTO transactions (transaction_pk, name, amount, category_fk, date_created)
        VALUES (?, ?, ?, ?, ?)
    """

INSERT_TEST_CATEGORY = """
        INSERT INTO categories (category_pk, name)
        VALUES (?, ?)
    """

CREATE_TRANSACTIONS_TEST_TABLE = """
        CREATE TABLE transactions (
            transaction_pk INTEGER PRIMARY KEY,
            name TEXT,
            amount REAL,
            category_fk TEXT,
            date_created INTEGER,
            FOREIGN KEY (category_fk) REFERENCES categories (category_pk)
        )
    """

CREATE_CATEGORIES_TEST_TABLE = """
        CREATE TABLE categories (
            category_pk TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def test_db(tmp_path):
    """Creates a temporary SQLite database for testing with both transactions and categories tables."""
    db_path = os.path.abspath(str(tmp_path / "test.db"))  # Convert to absolute path
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create `categories` table
    cursor.execute(CREATE_CATEGORIES_TEST_TABLE)

    # Create `transactions` table with a foreign key to `categories`
    cursor.execute(CREATE_TRANSACTIONS_TEST_TABLE)

    # Insert data into `categories` table, ensuring `category_fk` matches
    cursor.executemany(INSERT_TEST_CATEGORY, [
        ('2', 'Groceries'),
        ('4', 'Transport'),
        ('b952bfec-b4e0-4ec5-b621-0f46cbda4545', 'Therapy'),
        ('999', 'Unknown Category')
    ])

    # Insert test data into `transactions` table
    cursor.executemany(INSERT_TEST_TRANSACTIONS, [
        (1, 'Groceries', 50.00, '2', 1672531200),  # 2023-01-01
        (2, 'Bus Ticket', 2.50, '4', 1672617600),  # 2023-01-02
        (3, 'Therapy21', 100.00, 'b952bfec-b4e0-4ec5-b621-0f46cbda4545', 1672704000),  # 2023-01-03
        (4, 'Thing', 25.00, '999', 1672790400)  # 2023-01-04
    ])

    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def test_csv(tmp_path):
    """Creates a temporary directory for CSV file handling."""
    return os.path.abspath(str(tmp_path / "test.csv"))  # Convert to absolute path


@pytest.fixture
def exporter(test_db, test_csv, tmp_path):
    """Fixture to create a TransactionExporter instance."""
    # Ensure `test_csv` points to a location in the temporary pytest folder
    output_csv = os.path.abspath(str(tmp_path / "test.csv"))  # Convert to absolute path
    return TransactionExporter(test_db, output_csv)


@pytest.fixture
def g_handler():
    """Fixture to initialize the GoogleSheetsHandler with a mocked environment."""
    return GoogleSheetsHandler(SPREADSHEET_ID)
