"""
Module: config

Configuration constants for transaction export operations. This module centralizes
all configurations required for consistent and maintainable transaction processing,
such as column mappings, file naming conventions, category translations, and timezone settings.

Constants:
    - DATE_FILTER (str): Sets the starting date for filtering transactions in the format "YYYY-MM-DD".
    - COLUMN_MAPPING (dict): Maps database column names to their corresponding export CSV column names for clarity.
    - COLUMN_ORDER (list): Defines the desired order of columns in the export CSV based on the mapped column names.
    - CATEGORY_MAPPING (dict): Maps category foreign keys (`category_fk`) to human-readable category labels for better interpretation.
    - DB_FILE_PREFIX (str): Prefix that database `.sql` files must start with to be identified during file processing.
    - DB_FILE_SUFFIX (str): File extension for database files (typically "sql") used in file filtering.
    - SQL_FILE_NAME_REGEX (str): Regular expression pattern for matching database file names based on specific conventions.
    - TIMEZONE (str): Specifies the timezone for accurate date and time processing in the exported transactions.
    - NEW_TRANSACTION_FILE (str): Name of the CSV file where new transaction data is exported.
    - TRANSACTION_HISTORY_FILE (str): Name of the file that consolidates historical transaction data across exports.
    - PREVIOUS_TRANSACTION_HISTORY_FILE (str): Name of the backup file for transaction history prior to updates or deletions.

Usage:
    Import this module to access configuration constants for database interaction,
    file handling, naming conventions, and transaction exporting tasks.
"""
import logging

LOG_LEVEL = logging.INFO

# Constants for file lookup
DB_FILE_PREFIX: str = "cashew"  # Prefix for database `.sql` files
DB_FILE_SUFFIX: str = "sql"  # Suffix for database files

# Regex pattern to match filenames
SQL_FILE_NAME_REGEX = rf"^{DB_FILE_PREFIX}-db-v\d+-X\d+ \w+ \w+ \d+-\d+-\d+-\d+-\d+-\d+-\d+Z\.{DB_FILE_SUFFIX}$"
SQL_FILE_DATETIME_REGEX = r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d+Z"
SQL_FILE_DATETIME_FORMAT = "%Y-%m-%d-%H-%M-%S-%fZ"

# Delimiter used while reading and writing CSV files
CSV_DELIMITER = "\t"

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
    'category_name': 'kategoria',
    'date_created': 'data',
}

# Desired column order for the export (mapped names)
COLUMN_ORDER = ['id', 'opis', 'kwota', 'kategoria', 'data']

# List of category names
CATEGORIES = ['spożywcze', 'transport', 'przyjemności', 'inne', 'rachunki']
