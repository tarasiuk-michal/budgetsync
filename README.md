# Budget Sync

A Python-based application to process and synchronize transaction data. This tool provides functionality for exporting
transaction data from SQLite database files into CSV files or directly appending them to a Google Sheets document. It
automates locating the latest database files, processing transaction data, and generating output in a structured format.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Getting Started](#getting-started)
- [Requirements](#requirements)
- [Notes](#notes)

---

## Features

- Automatically identifies the most recent SQLite database file in the provided directory based on predefined naming
  conventions.
- Two primary modes of operation:
    - **Google Sheets Sync**: Appends filtered transactions directly to a Google Sheet.
    - **CSV Export** *(optional)*:
        - **`transactions.csv`**: Stores newly exported transactions.
        - **`transactions_history_previous.csv`**: A backup of prior transaction history for safekeeping.
        - **`transactions_history.csv`**: A combined file containing both old and new transaction data.
- Custom transaction creation and addition to Google Sheets (predefined examples available).
- Includes robust logging for tracking errors and the application's flow.

---

## Project Structure

```plaintext
.
├── main.py                        <-- Main entry point of the application
├── src/
│   ├── handlers/
│   │   ├── file_handler.py        <-- Handles file-related operations like finding the latest database file
│   │   ├── db_handler.py          <-- Manages database operations (e.g., data validation and SQL queries)
│   │   ├── google_sheets_handler.py <-- Handles interactions with Google Sheets API
│   ├── transaction_entity.py      <-- Transaction model for storing and processing transaction data
│   ├── transaction_exporter.py    <-- Contains logic for exporting transactions to CSV or Google Sheets
│   ├── utils/
│   │   ├── logger.py              <-- Provides centralized logging functionality
│   │   ├── csv_utils.py           <-- Utility functions for processing and manipulating CSV data
│   │   ├── formatter.py           <-- Formats transaction data (e.g., timestamps, amounts, and categories)
│   │   └── error_handling.py      <-- Decorators for logging and handling exceptions
├── tests/
│   ├── test_file_handler.py       <-- Unit tests for `file_handler.py`
│   ├── test_transaction_exporter.py <-- Unit tests for transaction export functionality
│   └── test_db_handler.py         <-- Unit tests for `db_handler.py`
├── README.md                      <-- Documentation for the project (this file)
├── requirements.txt               <-- List of required Python packages
└── LICENSE                        <-- Licensing information
```

---

### File and Folder Descriptions

#### **Top-Level Files**

1. **`main.py`**:  
   Main entry point of the application. Its primary responsibilities include:
    - Parsing command-line arguments.
    - Locating the most recent database file based on naming conventions.
    - Exporting transaction data to Google Sheets or generating local CSV files.
    - Includes optional functionality for adding predefined custom transactions.

2. **`README.md`**:  
   Documentation describing the purpose, setup, and usage of the application.

3. **`requirements.txt`**:  
   List of required Python libraries (e.g., `Google Sheets API`, `SQLite`, etc.).

4. **`LICENSE`**:  
   Licensing details for the project.

#### **`src/` (Source Code Directory)**

The source code is modularized for easier maintenance:

1. **Handlers**:
    - `file_handler.py`: Handles filesystem-level operations such as locating the latest `.sql` file.
    - `db_handler.py`: Encapsulates logic for fetching data from SQLite databases.
    - `google_sheets_handler.py`: Manages interactions with Google Sheets, including reading and appending rows.

2. **Utilities**:
    - `logger.py`: Provides centralized logging functionality for debugging and monitoring.
    - `csv_utils.py`: Handles CSV operations like backing up old files or processing rows.
    - `formatter.py`: Maps and formats transaction data fields (e.g., categories, timestamps).
    - `error_handling.py`: Implements custom decorators for exception handling.

3. **Core Logic**:
    - `transaction_entity.py`: Represents a single transaction and provides utilities for converting to various formats.
    - `transaction_exporter.py`: Contains the main transaction processing logic. Supports:
        - Fetching transactions from the database.
        - Comparing data against historic or Google Sheets records and identifying new entries.
        - Writing output to CSV or Google Sheets.

#### **`tests/` (Unit Tests Directory)**

Unit tests for individual components to ensure proper functionality (e.g., file handling, data processing, and database
interactions).

---

## Usage

### Command-Line Execution

Run the program using the following command:

```bash
python main.py <db_directory>
```

- `<db_directory>`: Required. Path to the directory containing the database files.

---

### Modes of Operation

#### 1. Appending to Google Sheets:

By default, the application will locate the latest database and append new transactions to a preconfigured Google Sheets
document. This requires a Google Sheets API setup.

#### 2. CSV Export *(Optional)*:

To enable the CSV export feature, uncomment the `fetch_and_export()` function in `main.py`. This will:

- Locate the latest database.
- Generate the following CSV files in the specified output directory:
    - `transactions.csv`
    - `transactions_history_previous.csv`
    - `transactions_history.csv`

---

### Example (Google Sheets):

Suppose the database files are stored in `/data/dbs/`.

```bash
python main.py /data/dbs/
```

What happens:

1. `TransactionExporter` fetches transactions from the latest database file in `/data/dbs/`.
2. Filters new transactions against existing rows in the Google Sheet.
3. Appends the new transactions to the sheet.

---

### Example (CSV Export):

Uncomment the `fetch_and_export()` function in `main.py` and re-run:

```bash
python main.py /data/dbs/ /data/exports/
```

---

### Adding Custom Transactions:

To add predefined transactions to the Google Sheet:

1. Uncomment the `add_custom()` function in `main.py`.
2. Run the script:
   ```bash
   python main.py
   ```

---

## Getting Started

### Requirements

- **Python Version**: 3.10 or newer
- **Required Libraries**: Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
   ```

2. Navigate to the project directory:
   ```bash
   cd budget_sync
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your Google Sheets API credentials. Refer to:
    - Google Cloud Console for enabling the API.
    - The `google_sheets_handler` module for authentication setup.

5. Run the program using the [Usage](#usage) instructions.

---

## Notes

- Ensure database files adhere to the naming convention `<DB_FILE_PREFIX>_<timestamp>.<DB_FILE_SUFFIX>`:
    - `DB_FILE_PREFIX` default: `cashew`
    - `DB_FILE_SUFFIX` default: `.sql`.
- Output (CSV or Sheets) depends on the mode of operation in `main.py`. Adjust configurations as needed.
- Logs are generated to provide detailed insights into actions performed during execution.