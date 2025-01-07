import os
import sqlite3
import sys
import pytest

from src.transaction_exporter import TransactionExporter

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def test_db(tmp_path):
    """Creates a temporary SQLite database for testing."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create schema
    cursor.execute("""
        CREATE TABLE transactions (
            transaction_pk INTEGER PRIMARY KEY,
            name TEXT,
            amount REAL,
            category_fk TEXT,
            date_created INTEGER
        )
    """)
    # Insert test data
    cursor.executemany("""
        INSERT INTO transactions (transaction_pk, name, amount, category_fk, date_created)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 'Groceries', 50.00, '2', 1672531200),  # 2023-01-01
        (2, 'Bus Ticket', 2.50, '4', 1672617600),  # 2023-01-02
        (3, 'Therapy', 100.00, 'b952bfec-b4e0-4ec5-b621-0f46cbda4545', 1672704000),  # 2023-01-03
        (4, 'Unknown Category', 25.00, '999', 1672790400),  # 2023-01-04
    ])
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def test_csv(tmp_path):
    """Creates a temporary directory for CSV file handling."""
    return tmp_path / "test.csv"


@pytest.fixture
def exporter(test_db, test_csv, tmp_path):
    """Fixture to create a TransactionExporter instance."""
    # Ensure `test_csv` points to a location in the temporary pytest folder
    output_csv = tmp_path / "test.csv"
    return TransactionExporter(str(test_db), str(output_csv))
