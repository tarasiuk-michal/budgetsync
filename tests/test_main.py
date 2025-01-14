import sys
from unittest.mock import patch

import config
from main import main


def test_main_script(mocker, test_db, test_csv):
    """Test the main script execution."""

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

    # Mock sys.exit to prevent actual exits
    with patch("sys.exit") as mock_exit:
        main()
        mock_exit.assert_not_called()  # Ensure sys.exit() didn't get called

    # Verify CSV writing behavior
    mock_write_csv.assert_called_once_with(test_csv, config.COLUMN_ORDER, [
        [1, '50,00', '01.01.2023', 'Groceries', 'spożywcze'],
        [2, '30,00', '02.01.2023', 'Fuel', 'inne']
    ])
