from unittest.mock import MagicMock, patch

import pytest

from src.handlers.google_sheets_handler import GoogleSheetsHandler

# Constants for testing
SPREADSHEET_ID = "test_spreadsheet_id"
SHEET_NAME = "Sheet1"
RANGE_NAME = f"{SHEET_NAME}!B10:G"
DATA_MOCK = [
    ["Row1-Col1", "Row1-Col2"],
    ["Row2-Col1", "Row2-Col2"],
]


@pytest.fixture
def g_handler():
    """Fixture to initialize the GoogleSheetsHandler with a mocked environment."""
    return GoogleSheetsHandler(SPREADSHEET_ID)


# 2. Test `read_transactions`
@patch("src.handlers.google_sheets_handler.GoogleSheetsHandler._authenticate_service")
def test_read_transactions(mock_auth_service, g_handler):
    """Test reading transactions from a given range."""
    # Mock the Google Sheets service
    mock_service = MagicMock()
    g_handler.service = mock_service

    # Mock response for `get` followed by `execute`
    mock_get = mock_service.spreadsheets().values().get
    mock_get.return_value.execute.return_value = {"values": DATA_MOCK}

    # Call the method
    result = g_handler.read_transactions(RANGE_NAME)

    # Assertions
    assert result == DATA_MOCK  # Check the returned data
    mock_auth_service.assert_called_once()  # Verify authentication was invoked
    mock_get.assert_called_once_with(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME
    )  # Verify 'get' is called with correct arguments


# 3. Test `append_transactions`
@patch("src.handlers.google_sheets_handler.GoogleSheetsHandler._authenticate_service")
def test_append_transactions(mock_auth_service, g_handler):
    """Test appending transactions to a given range."""
    mock_service = MagicMock()
    g_handler.service = mock_service
    transactions = [["NewRow1-Col1", "NewRow1-Col2"], ["NewRow2-Col1", "NewRow2-Col2"]]

    # Call the method
    g_handler.append_transactions(transactions, RANGE_NAME)

    # Assertions
    mock_auth_service.assert_called_once()  # Ensure authentication is triggered
    mock_service.spreadsheets().values().append.assert_called_once_with(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body={"values": transactions},
    )


# 4. Test `find_first_empty_row`
@patch("src.handlers.google_sheets_handler.GoogleSheetsHandler._authenticate_service")
def test_find_first_empty_row(mock_auth_service, g_handler):
    """Test finding the first empty row in a given range."""
    # Mock the Google Sheets service
    mock_service = MagicMock()
    g_handler.service = mock_service

    # Mock the behavior of the get() method
    mock_get = mock_service.spreadsheets().values().get
    mock_get.return_value.execute.return_value = {"values": DATA_MOCK}

    # Call the method
    result = g_handler.find_first_empty_row(RANGE_NAME)

    # Assertions
    # DATA_MOCK has 2 rows; thus, the first empty row is row 12
    assert result == f"{SHEET_NAME}!B12:G12"
    mock_auth_service.assert_called_once()  # Ensure authentication was called
    mock_get.assert_called_once_with(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME
    )  # Verify that the get() method was called once with the correct arguments


@pytest.mark.parametrize(
    "cell_reference, expected_result",
    [
        ("B10", ("B", 10)),
        ("A1", ("A", 1)),
        ("C", ("C", 1)),  # Defaults to row 1 if no number is given
    ],
)
def test_extract_column_and_row(cell_reference, expected_result):
    """Test extracting column and row from a cell reference."""
    column, row = GoogleSheetsHandler._extract_column_and_row(cell_reference)
    assert (column, row) == expected_result
