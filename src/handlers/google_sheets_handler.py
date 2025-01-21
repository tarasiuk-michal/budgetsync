import os
from typing import List, Optional

from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import SERVICE_ACCOUNT_FILE, MY_DEFAULT_RANGE
from src.utils.logger import Logging

# Define the required Google API scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsHandler(Logging):
    """Handles interactions with the Google Sheets API."""

    def __init__(self, spreadsheet_id: str, credentials_file: Optional[str] = None, token_file: Optional[str] = None):
        """
        Initialize the Google Sheets handler.

        Args:
            spreadsheet_id (str): The ID of the Google Spreadsheet to interact with.
            credentials_file (Optional[str]): Path to the client_secret.json file (for Installed App Flow).
            token_file (Optional[str]): Path to the token.json file for caching user credentials.
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None  # Cached instance of the Google Sheets API service
        self.logger.info("GoogleSheetsHandler initialized with Spreadsheet ID: %s", spreadsheet_id)

    def _authenticate_service(self) -> None:
        """Authenticate with Google Sheets API and initialize the service."""
        if self.service is not None:
            self.logger.debug("Google Sheets API service is already authenticated and initialized.")
            return

        try:
            if os.path.exists(SERVICE_ACCOUNT_FILE):
                self.logger.info("Authenticating with Service Account file: %s", SERVICE_ACCOUNT_FILE)
                credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            elif self.credentials_file and os.path.exists(self.credentials_file):
                self.logger.warning(
                    "Service account file not found. Fallback to Installed App Flow with credentials file: %s",
                    self.credentials_file)
                credentials = self._authenticate_with_installed_app_flow()
            else:
                self.logger.error("No valid credentials file found for authentication.")
                raise FileNotFoundError("No valid credentials file found for authentication.")

            self.service = build('sheets', 'v4', credentials=credentials)
            self.logger.info("Google Sheets API service successfully authenticated and initialized.")
        except Exception as error:
            self.logger.exception("Failed to authenticate and initialize Google Sheets API service: %s", error)
            raise

    def _authenticate_with_installed_app_flow(self):
        """Authenticate using Installed App Flow and cache credentials."""
        if not self.credentials_file:
            self.logger.error("A credentials file is required for Installed App Flow but not provided.")
            raise ValueError("A credentials file is required for Installed App Flow.")

        creds = None
        if self.token_file and os.path.exists(self.token_file):
            self.logger.info("Loading credentials from token file: %s", self.token_file)
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        if not creds or not creds.valid:
            self.logger.info("No valid credentials found. Initiating Installed App Flow.")
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            if self.token_file:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                self.logger.info("Credentials have been saved to the token file: %s", self.token_file)

        return creds

    def read_transactions(self, range_name: str = None) -> List[List[str]]:
        """
        Reads transactions from the specified cell range.

        Args:
            range_name (str): Range in A1 notation (e.g., "Sheet1!A1:D").

        Returns:
            List[List[str]]: A list of rows, where each row is a list of cell values.
        """
        self.logger.info("Attempting to read transactions from range: %s", range_name)
        self._authenticate_service()
        try:
            sheet = self.service.spreadsheets()
            if range_name is None:
                range_name = MY_DEFAULT_RANGE
                self.logger.info("Range not provided. Using default range: %s", MY_DEFAULT_RANGE)
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            if not values:
                self.logger.warning("No data found in the range: %s", range_name)
            else:
                self.logger.info("Read %d rows of data from range: %s", len(values), range_name)
            return values
        except HttpError as error:
            self.logger.exception("An error occurred while reading transactions: %s", error)
            return []

    def append_transactions(self, transactions: List[List[str]], range_name: str = None) -> None:
        """
        Appends a list of transactions to the specified range in the Google Sheet.
        
        Args:
            transactions (List[List[str]]): A list of rows, where each row represents a transaction to append.
            range_name (str, optional): The target range in A1 notation (e.g., "Sheet1!A1:D").
                                        If not provided, the first empty row will be determined automatically.
        """
        self.logger.info("Attempting to append %d rows to range: %s", len(transactions), range_name)
        self._authenticate_service()
        if not range_name:  # Automatically find the range in case it's not provided.
            range_name = self.find_first_empty_row()

        # Ensure we're logging the inputs just before making the call
        self.logger.info("Appending transactions: %s to range: %s", transactions, range_name)

        try:
            sheet = self.service.spreadsheets()
            body = {'values': transactions}

            # Ensure arguments to append match expected structure
            sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()
            self.logger.info("Successfully appended transactions to %s", range_name)
        except HttpError as error:
            self.logger.exception("An error occurred while appending transactions: %s", error)

    def find_first_empty_row(self, range_name: str = None) -> str:
        """
        Finds the first empty row in a given range and returns the new range in A1 notation.

        Args:
            range_name (str): Range in A1 notation (e.g., "Sheet1!B10:G").

        Returns:
            str: The range in A1 notation for the first empty row (e.g., "B25:G25").
        """
        self.logger.info("Attempting to find the first empty row in range: %s", range_name)
        self._authenticate_service()

        if not range_name:
            range_name = MY_DEFAULT_RANGE
            self.logger.info("Range not provided. Using default range: %s", MY_DEFAULT_RANGE)
        
        try:
            if '!' in range_name:
                # Split the range name into sheet and grid parts (e.g., "Sheet1!B10:G" -> Sheet1 and B10:G parts)
                sheet_name, range_parts = range_name.split("!", maxsplit=1)
            else:
                sheet_name = None
                range_parts = range_name

            column_range = range_parts.split(":")  # Extract the column range (e.g., "B10:G" -> ["B10", "G"])

            # Get only the starting column and the row number from the first part of the range, e.g., B10 -> column=B, start_row=10
            start_column, start_row = self._extract_column_and_row(column_range[0])

            # Fetch data from the range
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])

            # Determine the first empty row
            row_offset = len(values) + int(
                start_row) - 1  # Add the number of rows already fetched to the starting row - 1
            first_empty_row_range = f"{start_column}{row_offset + 1}:{column_range[1]}{row_offset + 1}"

            # Return the valid range in A1 notation
            if sheet_name:
                result_range = f"{sheet_name}!{first_empty_row_range}"
            else:
                result_range = f"{first_empty_row_range}"
            self.logger.info("First empty row range determined: %s", result_range)
            return result_range
        except HttpError as error:
            self.logger.exception("An error occurred while finding the first empty row: %s", error)
            raise

    @staticmethod
    def _extract_column_and_row(cell_reference: str) -> tuple:
        """
        Extracts the column and row from a cell reference (e.g., "B10").

        Args:
            cell_reference (str): The cell reference string (e.g., "B10").

        Returns:
            tuple: A tuple containing the column as a string and the row as an integer (e.g., ("B", 10)).
        """
        column = ''.join(char for char in cell_reference if char.isalpha())
        row = ''.join(char for char in cell_reference if char.isdigit())
        return column, int(row) if row else 1
