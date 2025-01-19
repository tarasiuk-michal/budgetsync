import sys

import config
from conftest import PATH_FETCH_TRANSACTIONS, PATH_WRITE_TO_CSV, PATH_READ_EXISTING_CSV
from main import main


def test_main_script(mocker, tmp_path):
    """Test the main script with dynamically generated pytest temp paths."""

    # Generate temporary files for database and CSV in the pytest-provided temp directory
    tmp_db_path = tmp_path / "cashew-mock-db-v46-X11 linux x86_64 2025-01-01-01-01-01-001Z.sql"
    tmp_csv_path = tmp_path / "mock_output.csv"

    tmp_db_path.touch()
    tmp_csv_path.touch()

    # Simulate CLI arguments
    sys.argv = ['main.py', str(tmp_path), str(tmp_path)]

    # Mock `os.path.isfile` to simulate the presence of the database file
    mocker.patch("os.path.isfile", return_value=True)

    # Mock DBHandler.fetch_transactions to simulate data fetching
    mocker.patch(PATH_FETCH_TRANSACTIONS, return_value=[
        (1, 'Groceries', 50.00, '2', 1672531200),
        (2, 'Fuel', 30.00, '3', 1672617600)
    ])

    # Mock CSVHandler.read_existing_csv to simulate no existing data
    mocker.patch(PATH_READ_EXISTING_CSV, return_value=[])

    # Mock CSVHandler.write_to_csv to verify the expected behavior
    mock_write_csv = mocker.patch(PATH_WRITE_TO_CSV)

    main()

    # Verify correct data was written to CSV
    expected_data = [
        ['1', 'Groceries', '50,00', 'inne', '2023-01-01'],
        ['2', 'Fuel', '30,00', 'inne', '2023-01-02'],
    ]
    mock_write_csv.assert_called_once_with(str(tmp_csv_path), config.COLUMN_ORDER, expected_data)
