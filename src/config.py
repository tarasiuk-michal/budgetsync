import logging

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

# Logger configuration
LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'datefmt': '%H:%M:%S',
}
