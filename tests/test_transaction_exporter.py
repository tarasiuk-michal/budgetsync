import logging
import os

import config
from conftest import PATH_READ_EXISTING_CSV, PATH_FETCH_TRANSACTIONS, OS_PATH_EXISTS, OS_REMOVE, \
    OS_RENAME, TEST_ROWS, INVALID_TEST_ROWS


def test_process_rows(exporter):
    """Test processing of rows into the correct format."""
    rows = INVALID_TEST_ROWS
    processed = exporter.process_rows(rows)

    assert len(processed) == 2
    assert processed[0] == [1, 'Groceries', '50,00', 'spożywcze', '2023-01-01']
    assert processed[1][3] == 'inne'  # Check default category for unknown


def test_fetch_and_export(mocker, exporter, tmp_path):
    """Test the end-to-end fetching and exporting process."""
    # Mock fetch_transactions to return dummy transaction data
    mocker.patch(PATH_FETCH_TRANSACTIONS, return_value=TEST_ROWS)

    # Mock read_existing_csv to simulate no existing data
    mocker.patch(PATH_READ_EXISTING_CSV, return_value=list())

    # Create output directory with `tmp_path`
    mock_output_dir = tmp_path / "test_output"
    mock_output_dir.mkdir(parents=True, exist_ok=True)

    # Replace exporter's output directory with the mocked one
    exporter.output_dir = str(mock_output_dir)

    # Call the method to fetch and export
    exporter.fetch_and_export()

    output_csv = exporter.output_dir + '/transactions.csv'
    print(output_csv)
    assert os.path.exists(output_csv)
    # Open the CSV file and assert its contents
    with open(output_csv, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Check if file writing occurred and content validity
    assert len(lines) > 1  # Includes headers + data rows
    assert '1\tGroceries\t50,00\tspożywcze\t2023-01-01' in lines[1]
    assert '2\tFuel\t30,00\ttransport\t2023-01-02' in lines[2]


def test_process_rows_logging(exporter, caplog):
    rows = [(1, 'Test', None, '999', 1672531200)]  # Missing data for kwota

    # Set caplog level to ensure it captures warnings
    caplog.set_level(logging.WARNING)

    # Call the process_rows function
    exporter.process_rows(rows)

    # Debug logs for verification
    print(caplog.text)  # Temporary - see if logging is captured at all in the test

    # Validate that warnings for skipped rows are logged
    assert "Skipping row" in caplog.text
    assert "NoneType" in caplog.text


def test_output_to_multiple_files_integration(tmp_path, exporter):
    """Test writing transactions and backing up files without mocks."""
    # Prepare test data and file paths
    rows = TEST_ROWS
    mock_file_paths = {
        'transactions_file': str(tmp_path / "transactions.csv"),
        'history_file': str(tmp_path / "transactions_history.csv"),
        'history_backup_file': str(tmp_path / "transactions_history_backup.csv"),
    }

    # Write transactions
    exporter.write_transactions(mock_file_paths, rows)

    # Check that files are created
    assert os.path.exists(mock_file_paths['transactions_file']), "Transactions file was not created."
    assert os.path.exists(mock_file_paths['history_file']), "History file was not created."

    # Call backup and check the backup result
    exporter.backup_history_file(mock_file_paths['history_file'], mock_file_paths['history_backup_file'])
    assert not os.path.exists(mock_file_paths['history_file']), "History file was not backed up."
    assert os.path.exists(mock_file_paths['history_backup_file']), "Backup file was not created."


def test_define_file_paths(exporter):
    """Test defining file paths."""
    file_paths = exporter.define_file_paths()
    assert 'transactions_file' in file_paths
    assert 'history_file' in file_paths
    assert 'history_backup_file' in file_paths
    assert file_paths['transactions_file'].endswith(config.NEW_TRANSACTION_FILE)
    assert file_paths['history_file'].endswith(config.TRANSACTION_HISTORY_FILE)
    assert file_paths['history_backup_file'].endswith(config.PREVIOUS_TRANSACTION_HISTORY_FILE)


def test_define_file_paths_with_custom_output(exporter):
    """Test defining file paths with custom output."""
    exporter.output_csv = 'custom_output'
    file_paths = exporter.define_file_paths()
    assert 'transactions_file' in file_paths
    assert 'history_file' in file_paths


def test_prepare_new_transactions_no_history_file(mocker, exporter):
    """Test preparing new transactions when no history file exists."""
    mocker.patch(OS_PATH_EXISTS, return_value=False)
    processed_data = [(1, 'Groceries', 50.00, '2', 1672531200),
                      (2, 'Fuel', 30.00, '3', 1672617600)]
    new_transactions = exporter.prepare_new_transactions('dummy_history_file.csv', processed_data)
    assert new_transactions == processed_data  # All transactions are new


def test_prepare_new_transactions_with_history_file(mocker, exporter):
    """Test preparing new transactions with existing history."""
    mocker.patch(OS_PATH_EXISTS, side_effect=lambda x: x == 'history_file.csv')
    mock_read_csv = mocker.patch(PATH_READ_EXISTING_CSV, return_value={(1, 'Groceries', 50.00, '2', 1672531200)})
    processed_data = [(1, 'Groceries', 50.00, '2', 1672531200),
                      (2, 'Fuel', 30.00, '3', 1672617600)]
    new_transactions = exporter.prepare_new_transactions('history_file.csv', processed_data)
    assert new_transactions == [(2, 'Fuel', 30.00, '3', 1672617600)]  # Only the second transaction is new
    mock_read_csv.assert_called_once_with('history_file.csv')


def test_backup_history_file_existing_backup(mocker, exporter):
    """Test backing up the history file when the backup exists."""
    mocker.patch('os.path.exists', side_effect=lambda x: x in ['history_file.csv', 'history_backup_file.csv'])

    mock_remove = mocker.patch(OS_REMOVE)
    mock_rename = mocker.patch(OS_RENAME)

    exporter.backup_history_file('history_file.csv', 'history_backup_file.csv')

    mock_remove.assert_called_once_with('history_backup_file.csv')  # Ensure the old backup is removed
    mock_rename.assert_called_once_with('history_file.csv', 'history_backup_file.csv')  # Ensure the backup is created


def test_backup_history_file_no_existing_backup(mocker, exporter):
    """Test backing up the history file when no backup exists."""
    mocker.patch(OS_PATH_EXISTS, side_effect=lambda x: False)
    mock_rename = mocker.patch(OS_RENAME)

    exporter.backup_history_file('history_file.csv', 'history_backup_file.csv')

    mock_rename.assert_not_called()


def test_write_transactions(mocker, exporter):
    """Test writing transactions with proper formatting and updating history."""
    # Mock necessary methods
    # Mock CSVHandler.write_to_csv to track its calls
    mock_write_csv = mocker.patch("src.handlers.csv_handler.CSVHandler.write_to_csv")

    # Mock CSVHandler.read_existing_csv to return raw rows
    mock_read_csv = mocker.patch(
        "src.handlers.csv_handler.CSVHandler.read_existing_csv",
        return_value=[
            (1, 'Groceries', 50.00, '2', 1672531200)  # Match unprocessed raw row format
        ]
    )

    # Mock the row mapping function `map_row` to ensure consistent transformed results
    mock_map_row = mocker.patch(
        "src.transaction_exporter.TransactionExporter.map_row",
        side_effect=lambda row: {  # Map raw rows to dict outputs
            'id': str(row[0]),
            'opis': row[1],
            'kwota': f"{row[2]:,.2f}".replace('.', ','),
            'kategoria': 'inne',  # Given there's no category lookup, default is 'inne'
            'data': '2023-01-01' if row[4] == 1672531200 else '2023-01-02',
        }
    )

    # Define test inputs
    file_paths = {
        'transactions_file': 'transactions.csv',
        'history_file': 'transactions_history.csv'
    }
    new_transactions = [
        (2, 'Fuel', 30.00, '3', 1672617600)  # A new raw transaction from the database
    ]

    # Run the method
    exporter.write_transactions(file_paths, new_transactions)

    # Verify new transactions were written to `transactions.csv`
    expected_transactions = [
        ['2', 'Fuel', '30,00', 'inne', '2023-01-02']
    ]
    mock_write_csv.assert_any_call('transactions.csv', config.COLUMN_ORDER, expected_transactions)

    # Verify `read_existing_csv` was called once for the history file
    mock_read_csv.assert_called_once_with('transactions_history.csv')

    # Verify history file was updated with existing + new transactions
    expected_history = [
        ['1', 'Groceries', '50,00', 'inne', '2023-01-01'],  # Existing transaction
        ['2', 'Fuel', '30,00', 'inne', '2023-01-02']  # New transaction
    ]
    mock_write_csv.assert_any_call('transactions_history.csv', config.COLUMN_ORDER, expected_history)

    # Ensure the map_row method was called for each row
    mock_map_row.assert_any_call((1, 'Groceries', 50.00, '2', 1672531200))  # From `read_existing_csv`
    mock_map_row.assert_any_call((2, 'Fuel', 30.00, '3', 1672617600))  # From `new_transactions`


def test_logging_on_process_rows_logging(exporter, caplog):
    """Test logging during the processing of rows."""
    rows = [(1, 'Invalid', None, '999', 1672531200)]  # Invalid data
    caplog.set_level(logging.WARNING)

    exporter.process_rows(rows)

    assert "Skipping row" in caplog.text
    assert "NoneType" in caplog.text
