import os
from typing import List

from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import SERVICE_ACCOUNT_FILE

# If modifying these SCOPES, delete the token.json file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsHandler:
    """Handles interactions with Google Sheets API."""

    def __init__(self, credentials_file: str, token_file: str, spreadsheet_id: str):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.spreadsheet_id = spreadsheet_id
        self.service = self._authenticate()

    @staticmethod
    def setup_google_sheets_service():
        """
           Authenticate and initialize Google Sheets API service.
           """
        # Authenticate using the service account JSON
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # Build the Sheets API service
        service = build("sheets", "v4", credentials=credentials)
        return service

    @staticmethod
    def read_google_sheets(sheet_id, range_name):
        """
           Read data from a Google Sheet.
           """
        service = GoogleSheetsHandler.setup_google_sheets_service()
        sheet = service.spreadsheets()

        # Read data from the provided range
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get("values", [])

        if not values:
            print("No data found.")
        else:
            print("Data retrieved from Google Sheets:")
            for row in values:
                print(row)

        return values

    def _authenticate(self):
        """Authenticate and return the Google Sheets API service."""
        creds = None
        # Load existing credentials
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        # If no valid credentials are available, authorize the user
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for future use
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        return build('sheets', 'v4', credentials=creds)

    def read_transactions(self, range_name: str) -> List[List[str]]:
        """
        Read transactions from the specified range.
        
        Args:
            range_name (str): The range of cells to read (e.g., "Sheet1!A1:D").
        
        Returns:
            List[List[str]]: A list of rows, where each row is a list of cell values.
        """
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            return result.get('values', [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def append_transactions(self, range_name: str, transactions: List[List[str]]) -> None:
        """
        Append new transactions to the sheet.
        
        Args:
            range_name (str): The target range for appending data (e.g., "Sheet1!A1:D").
            transactions (List[List[str]]): A list of rows to append to the sheet.
        """
        try:
            sheet = self.service.spreadsheets()
            body = {
                'values': transactions
            }
            sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            print("Transactions successfully appended.")
        except HttpError as error:
            print(f"An error occurred: {error}")

    def find_transaction(self, range_name: str, transaction_id: str) -> List[str]:
        """
        Search for a transaction in the sheet by transaction ID.
        
        Args:
            range_name (str): The range of cells to search within (e.g., "Sheet1!A1:D").
            transaction_id (str): The ID of the transaction to search for.
        
        Returns:
            List[str]: The matching row, or an empty list if not found.
        """
        transactions = self.read_transactions(range_name)
        for row in transactions:
            if row and row[0] == transaction_id:  # Assuming transaction IDs are in the first column
                return row
        return []
