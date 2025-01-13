"""
Module: config

Configuration constants for transaction export operations. This module centralizes
all configurations required for consistent and maintainable transaction processing,
such as column mappings, file naming conventions, and category translations.

Constants:
    - DATE_FILTER (str): Sets the starting date for filtering transactions in the format "YYYY-MM-DD".
    - COLUMN_MAPPING (dict): Maps database column names to their corresponding export CSV column names.
    - COLUMN_ORDER (list): Defines the order of columns in the export CSV based on the mapped column names.
    - CATEGORY_MAPPING (dict): Maps category foreign keys (`category_fk`) to human-readable category labels.
    - DB_FILE_PREFIX (str): Prefix that database `.sql` files must start with to be identified.
    - DB_FILE_SUFFIX (str): File extension for database files (typically "sql").
    - TIMEZONE (str): Specifies the timezone for date processing in the exported transactions.
    - NEW_TRANSACTION_FILE (str): Name of the CSV file for new transactions.
    - TRANSACTION_HISTORY_FILE (str): Name of the file that consolidates all transaction history.
    - PREVIOUS_TRANSACTION_HISTORY_FILE (str): Name of the backup file for transaction history prior to updates.

Usage:
    Import this module to access configuration constants for database interaction,
    file handling, and transaction exporting tasks.
"""

# Constants for file lookup
DB_FILE_PREFIX: str = "cashew"  # Prefix for database `.sql` files
DB_FILE_SUFFIX: str = "sql"  # Suffix for database files

# Constants for output CSV file naming
NEW_TRANSACTION_FILE: str = "transactions.csv"
TRANSACTION_HISTORY_FILE: str = "transactions_history.csv"
PREVIOUS_TRANSACTION_HISTORY_FILE: str = "previous_transactions_history.csv"

# Constants for the configuration
DATE_FILTER: str = '2025-01-01'

# Define the timezone for the project
TIMEZONE: str = "Europe/Warsaw"

# Mapping of database column names to export file column names
COLUMN_MAPPING = {
    'transaction_pk': 'id',
    'name': 'opis',
    'amount': 'kwota',
    'category_fk': 'kategoria',
    'date_created': 'data',
}

# Desired column order for the export (mapped names)
COLUMN_ORDER = ['id', 'kwota', 'data', 'opis', 'kategoria']

# Mapping for category_fk values
CATEGORY_MAPPING = {
    '2': 'spożywcze',
    '4': 'transport',
    'b952bfec-b4e0-4ec5-b621-0f46cbda4545': 'terapia',
    'a15d9070-bd80-4079-8764-08445f019730': 'transport',
}
