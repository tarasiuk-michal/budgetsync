import unittest
from unittest.mock import patch, MagicMock

from src.transaction_exporter import TransactionExporter


class TestTransactionExporter(unittest.TestCase):

    def setUp(self):
        """Set up basic test fixtures."""
        self.db_file = 'test_db.sqlite'
        self.output_dir = '/test_output'
        self.exporter = TransactionExporter(self.db_file, self.output_dir)

    @patch('os.path.abspath')
    def test_init(self, mock_abspath):
        """Test the initialization of TransactionExporter."""
        # Properly handle slashes in the returned path to avoid double slashes
        mock_abspath.side_effect = lambda x: f'/absolute/{x.lstrip("/")}'

        exporter = TransactionExporter('test_db.sqlite', '/test_output')
        self.assertEqual(exporter.db_file, '/absolute/test_db.sqlite')
        self.assertEqual(exporter.output_dir, '/absolute/test_output')

    @patch('src.handlers.db_handler.DBHandler.fetch_transactions', return_value=[])
    @patch('src.handlers.google_sheets_handler.GoogleSheetsHandler.read_transactions', return_value=None)
    def test_fetch_and_append_no_transactions(self, mock_read_transactions, mock_fetch_transactions):
        """
        Test fetch_and_append when no transactions are fetched from the database.
        """
        sheet_handler_mock = MagicMock()

        self.exporter.fetch_and_append(self.db_file, sheet_handler_mock)

        # Ensure DBHandler.fetch_transactions was called
        mock_fetch_transactions.assert_called_once()
        # Ensure no writes to the sheet are attempted
        sheet_handler_mock.append_transactions.assert_not_called()

    @patch('src.handlers.db_handler.DBHandler.fetch_transactions')
    @patch('src.handlers.google_sheets_handler.GoogleSheetsHandler.read_transactions')
    @patch('src.handlers.google_sheets_handler.GoogleSheetsHandler.append_transactions')
    def test_fetch_and_append_new_transactions(self, mock_append_transactions, mock_read_transactions,
                                               mock_fetch_transactions):
        """
        Test fetch_and_append when new transactions are fetched and appended to the sheet.
        """
        # Mock database transactions (fetching)
        mock_fetch_transactions.return_value = [
            (1, 'Description1', 100.0, 'transport', 1696118400),  # UNIX timestamp (e.g., 2023-10-01)
            (2, 'Description2', 200.0, 'Category2', 1696204800),  # UNIX timestamp (e.g., 2023-10-02)
        ]

        # Mock existing transactions in the sheet
        mock_read_transactions.return_value = [['1', 'Description1', '100,00', 'transport', '2023-10-01']]

        # GoogleSheetsHandler instance (mock_append_transactions is automatically tied to this mock)
        sheet_handler_mock = MagicMock()
        sheet_handler_mock.append_transactions = mock_append_transactions

        # Call method
        self.exporter.fetch_and_append(self.db_file, sheet_handler_mock)

        # Ensure expected new transactions are appended
        mock_append_transactions.assert_called_once_with(
            [['1', 'Description1', '100,00', 'transport', '2023-10-01'],
             ['2', 'Description2', '200,00', 'inne', '2023-10-02']]
        )

    @patch('os.path.exists', return_value=False)
    @patch('src.handlers.csv_handler.CSVHandler.read_existing_csv', return_value=[])
    @patch('src.handlers.db_handler.DBHandler.fetch_transactions')
    def test_extract_new_transactions(self, mock_fetch_transactions, mock_read_existing_csv, mock_exists):
        """
        Test extract_new_transactions to ensure it identifies only new transactions.
        """
        # Mock fetched transactions from the database
        mock_fetch_transactions.return_value = [
            (1, 'Description1', 100.0, 'Category1', 1696118400),
            (2, 'Description2', 200.0, 'Category2', 1696204800),
        ]

        # Call extract_new_transactions with empty history
        new_transactions = self.exporter.extract_new_transactions('history.csv', mock_fetch_transactions.return_value)

        # Verify that all transactions are new
        self.assertEqual(new_transactions, mock_fetch_transactions.return_value)

    @patch('shutil.copy')
    @patch('os.path.exists', side_effect=lambda x: x == 'history.csv')
    def test_backup_history_file(self, mock_exists, mock_copy):
        """
        Test backup_history_file to verify the correct handling of history files.
        """
        history_file = 'history.csv'
        backup_file = 'history_backup.csv'

        self.exporter.backup_history_file(history_file, backup_file)

        # Ensure shutil.copy is called only when the history file exists
        mock_copy.assert_called_once_with(history_file, backup_file)

    @patch('src.handlers.csv_handler.CSVHandler.rewrite_csv')
    @patch('src.handlers.csv_handler.CSVHandler.append_to_csv')
    def test_write_transactions(self, mock_append_csv, mock_rewrite_csv):
        """
        Test write_transactions to verify writing to the appropriate files.
        """
        file_paths = {
            'transactions_file': 'new_transactions.csv',
            'history_file': 'history.csv',
            'history_backup_file': 'history_backup.csv',
        }
        new_transactions = [
            (1, 'Description1', 100.0, 'Category1', 1696118400),
            (2, 'Description2', 200.0, 'Category2', 1696204800),
        ]

        self.exporter.write_transactions(file_paths, new_transactions)

        # Ensure new transactions are written to the transactions file
        mock_rewrite_csv.assert_called_once()
        # Ensure new transactions are appended to the history file
        mock_append_csv.assert_called_once()
