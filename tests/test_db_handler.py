from src.db_handler import DBHandler

def test_fetch_transactions(test_db):
    """Test that transactions are fetched properly from the database."""
    db_path = str(test_db)
    date_filter = "2023-01-01"  # Date after records should exist

    rows = DBHandler.fetch_transactions(db_path, date_filter)

    assert len(rows) == 3  # Number of rows should match the seed data
    assert rows.__contains__((2, 'Bus Ticket', 2.5, '4', 1672617600))
    assert rows.__contains__((3, 'Therapy', 100.00, 'b952bfec-b4e0-4ec5-b621-0f46cbda4545', 1672704000))
    assert rows.__contains__((4, 'Unknown Category', 25.00, '999', 1672790400))