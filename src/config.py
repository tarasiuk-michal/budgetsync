"""
Module: config

This module contains configuration constants for transaction export operations, such as
column mappings, export order, and category translations.

Constants:
    - DATE_FILTER: Defines the starting date for filtering transactions (format: "YYYY-MM-DD").
    - COLUMN_MAPPING: Maps database column names to export CSV column names.
    - COLUMN_ORDER: Specifies the desired column order in the export CSV.
    - CATEGORY_MAPPING: Maps category foreign keys (`category_fk`) to human-readable category names.

Usage:
    Import this module to access configurations for database row mapping, filtering, or CSV
    export formatting.

"""

"""
config.py

This module contains global configuration settings and constants used throughout the project.
It includes mappings, column orders, filters, and timezone settings that allow for consistent and centralized project behavior.
"""

# Constants for the configuration
DATE_FILTER = '2025-01-01'

# Define the timezone for the project
TIMEZONE = "Europe/Warsaw"

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
