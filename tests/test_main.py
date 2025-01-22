import sys
from unittest.mock import MagicMock
from unittest.mock import patch

from main import add_custom, fetch_and_append
from main import fetch_and_export


@patch('src.handlers.google_sheets_handler.GoogleSheetsHandler.append_transactions')
def test_add_custom(mock_append_transactions):
    add_custom()
    mock_append_transactions.assert_called_once()

    res, args = mock_append_transactions.call_args
    transactions = res[0]

    expected_transactions = [
        ['', 'wyrównanie', '-7,50', 'przyjemności', '2025-01-20', 'Michał'],
        ['', 'wyrównanie', '-7,50', 'przyjemności', '2025-01-20', 'Daga']
    ]

    assert transactions == expected_transactions


@patch('src.handlers.file_handler.FileHandler.find_latest_sql_file')
@patch('src.handlers.file_handler.FileHandler.get_db_directory')
@patch('src.handlers.file_handler.FileHandler.get_output_directory')
@patch('src.transaction_exporter.TransactionExporter.fetch_and_export')
def test_fetch_and_export(mock_fetch_and_export, mock_get_output_directory, mock_get_db_directory,
                          mock_find_latest_sql_file, tmp_path):
    # Use pytest's tmp_path for a temporary directory
    temp_dir = tmp_path / "db"
    temp_dir.mkdir(parents=True, exist_ok=True)
    latest_sql_file = temp_dir / "latest.sql"
    latest_sql_file.touch()  # Create an empty file

    # Mock returns with tmp_path-equivalent directories
    mock_get_db_directory.return_value = str(temp_dir)
    mock_get_output_directory.return_value = str(tmp_path / "output")
    mock_find_latest_sql_file.return_value = str(latest_sql_file)

    # Call the method
    fetch_and_export()

    # Assertions
    mock_fetch_and_export.assert_called_once()  # Ensure export was invoked
    mock_find_latest_sql_file.assert_called_with(str(temp_dir))


def test_fetch_and_append():
    with patch('main.FileHandler') as MockFileHandler, \
            patch('main.GoogleSheetsHandler') as MockGoogleSheetsHandler, \
            patch('main.TransactionExporter') as MockTransactionExporter:
        # Mock FileHandler's methods
        MockFileHandler.get_db_directory.return_value = '/mock/db_directory'
        MockFileHandler.find_latest_sql_file.return_value = '/mock/latest_db_file.sql'

        # Mock GoogleSheetsHandler
        mock_gs_handler = MockGoogleSheetsHandler.return_value
        mock_gs_handler.append_transactions = MagicMock()

        # Mock TransactionExporter
        mock_exporter_instance = MockTransactionExporter.return_value
        mock_exporter_instance.fetch_and_append = MagicMock()

        # Call the function
        fetch_and_append()

        # Assertions
        MockFileHandler.get_db_directory.assert_called_once_with(sys.argv)
        MockFileHandler.find_latest_sql_file.assert_called_once_with('/mock/db_directory')
        mock_exporter_instance.fetch_and_append.assert_called_once_with('/mock/latest_db_file.sql', mock_gs_handler)


def test_fetch_and_append_with_real_instance(tmp_path):
    temp_db_dir = tmp_path / "db"
    temp_db_dir.mkdir(parents=True, exist_ok=True)
    latest_sql_file = temp_db_dir / "latest.sql"
    latest_sql_file.touch()

    with patch('src.handlers.file_handler.FileHandler.find_latest_sql_file', return_value=str(latest_sql_file)), \
            patch('src.handlers.file_handler.FileHandler.get_db_directory', return_value=str(temp_db_dir)), \
            patch('src.transaction_exporter.TransactionExporter.fetch_and_append') as mock_fetch_and_append:
        # Use a real instance of GoogleSheetsHandler (only for debugging)
        fetch_and_append()

        mock_fetch_and_append.assert_called_once()
