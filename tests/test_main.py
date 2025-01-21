import datetime
import sys
from unittest.mock import patch, MagicMock

from main import add_custom, fetch_and_export, fetch_and_append


def test_add_custom():
    # Mock GoogleSheetsHandler
    with patch('main.GoogleSheetsHandler') as MockGoogleSheetsHandler:
        mock_handler_instance = MockGoogleSheetsHandler.return_value
        mock_handler_instance.append_transactions = MagicMock()

        # Call the function
        add_custom()

        # Ensure 'append_transactions' is called with the right data
        expected_calls = [
            ['wyrównanie', -7.5, 'PRZYJEMNOŚCI', datetime.datetime(2025, 1, 20), 'Michał'],
            ['wyrównanie', -7.5, 'PRZYJEMNOŚCI', datetime.datetime(2025, 1, 20), 'Daga']
        ]
        mock_handler_instance.append_transactions.assert_called_once()


def test_fetch_and_export():
    with patch('main.FileHandler') as MockFileHandler, \
            patch('main.TransactionExporter') as MockTransactionExporter, \
            patch('main.os.makedirs'), \
            patch('main.logger') as MockLogger:
        # Mock FileHandler's methods
        MockFileHandler.get_db_directory.return_value = '/mock/db_directory'
        MockFileHandler.get_output_directory.return_value = '/mock/output_directory'
        MockFileHandler.find_latest_sql_file.return_value = '/mock/latest_db_file.sql'

        # Mock TransactionExporter
        mock_exporter_instance = MockTransactionExporter.return_value
        mock_exporter_instance.fetch_and_export = MagicMock()

        # Call the function
        fetch_and_export()

        # Assertions
        MockFileHandler.get_db_directory.assert_called_once_with(sys.argv)
        MockFileHandler.get_output_directory.assert_called_once_with(sys.argv)
        MockFileHandler.find_latest_sql_file.assert_called_once_with('/mock/db_directory')
        mock_exporter_instance.fetch_and_export.assert_called_once()


def test_fetch_and_append():
    with patch('main.FileHandler') as MockFileHandler, \
            patch('main.GoogleSheetsHandler') as MockGoogleSheetsHandler, \
            patch('main.TransactionExporter') as MockTransactionExporter, \
            patch('main.logger') as MockLogger:
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
