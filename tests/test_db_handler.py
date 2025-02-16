from unittest.mock import patch

from src.handlers.db_handler import DBHandler


def test_fetch_transactions(test_db):
    """Test that transactions are fetched properly from the database."""
    db_path = str(test_db)
    date_filter = "2023-01-01"  # Date after records should exist

    rows = DBHandler.fetch_transactions(db_path, date_filter)

    assert len(rows) == 3  # Number of rows should match the seed data
    assert rows.__contains__((2, 'Bus Ticket', 2.5, 'Transport', 1672617600))
    assert rows.__contains__((3, 'Therapy21', 100.00, 'Therapy', 1672704000))
    assert rows.__contains__((4, 'Thing', 25.00, 'Unknown Category', 1672790400))


@patch('sqlite3.connect')
def test_fetch_transactions_no_data(mock_connect):
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = []  # Mock empty query result
    transactions = DBHandler.fetch_transactions("/mock/db/path", "2022-01-01")
    assert transactions == []
