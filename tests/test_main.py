import pytest


def test_main_script(mocker, test_db, test_csv):
    """Test the main script execution."""
    from src.main import main
    import sys

    # Simulate command-line arguments
    sys.argv = ['main.py', str(test_db), str(test_csv)]

    # Mock DBHandler.fetch_transactions to simulate fetching transaction data
    mocker.patch(
        'src.db_handler.DBHandler.fetch_transactions',
        return_value=[
            (1, 'Groceries', 50.00, '2', 1672531200),
            (2, 'Fuel', 30.00, '3', 1672617600),
        ]
    )

    # Mock CSVHandler.read_existing_csv to simulate no existing data
    mocker.patch('src.csv_handler.CSVHandler.read_existing_csv', return_value=set())

    # Mock CSVHandler.write_to_csv to verify behavior
    mock_write_csv = mocker.patch('src.csv_handler.CSVHandler.write_to_csv')

    try:
        main()

        # Assert that `write_to_csv` was called with the correct arguments
        mock_write_csv.assert_called_once_with(
            str(test_csv),
            ['id', 'kwota', 'data', 'opis', 'kategoria'],
            [[1, '50,00', '01.01.2023', 'Groceries', 'spożywcze'],
             [2, '30,00', '02.01.2023', 'Fuel', 'inne']]
        )
    except Exception as e:
        pytest.fail(f"Main script failed: {e}")
