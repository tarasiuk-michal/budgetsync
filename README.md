# Budget sync

A Python-based application that facilitates the export of transaction data from SQLite database files into CSV format.
This tool automates the process of locating and working with the latest database files and generating transaction
reports.

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
- Exports transaction data into standardized CSV files, including:
    - **`transactions.csv`**: Contains the latest exported transactions.
    - **`transactions_history_previous.csv`**: A backup of the prior transaction history for safekeeping.
    - **`transactions_history.csv`**: A combined file containing both old and new transaction data.
- Includes robust logging to track errors and application flow.

---

## Project Structure

```plaintext
.
├── main.py                        <-- Main entry point of the application
├── src/
│   ├── file_handler.py            <-- Handles file-related operations, such as finding the latest SQL file
│   ├── db_handler.py              <-- Manages database-specific operations (e.g. validating and querying databases)
│   ├── transaction_exporter.py    <-- Contains the main logic for exporting transactions to CSV files
│   ├── utils/
│   │   ├── logger.py              <-- Provides logging functionality for the application
│   │   └── csv_utils.py           <-- Additional helper functions for handling and manipulating CSV data
├── tests/
│   ├── test_file_handler.py       <-- Unit tests for file handling functions (e.g., locating database files)
│   ├── test_transaction_exporter.py <-- Unit tests for the transaction export functionality
│   └── test_db_handler.py         <-- Unit tests for database operation functions
├── README.md                      <-- Documentation for the project (this file)
├── requirements.txt               <-- List of required Python packages
└── LICENSE                        <-- Licensing information
```

---

### File and Folder Descriptions

#### **Top-Level Files**

- `main.py`: This is the main entry point script of the application. It handles:
    - Parsing and validating command-line arguments.
    - Locating the most recent database file with specific naming conventions.
    - Instantiating the transaction export and invoking the logic defined in the core scripts.

- `README.md`: Provides a detailed overview of the project, including setup, usage, and documentation.

- `requirements.txt`: Contains a list of external libraries or dependencies required by the application (e.g., `SQLite`,
  `logging`, `pandas`, etc.).

- `LICENSE`: Details the licensing terms of the project.

---

#### **`src/` (Source Code Directory)**

The source code is organized into logical modules for ease of maintenance and extensibility:

1. **Core Modules**
    - `file_handler.py`: Handles finding and validating the latest database file in a given path. Includes utilities
      such as sorting files based on timestamps or prefixes.
    - `db_handler.py`: Contains logic for querying SQLite databases and validating database integrity.
    - `transaction_exporter.py`: Implements the key functionality for:
        - Querying the database for transaction data.
        - Writing that data into the designated CSV files:
            - `transactions.csv`
            - `transactions_history_previous.csv`
            - `transactions_history.csv`

2. **Utilities**
    - `logger.py`: Centralized logging functionality for the application. Configures error, debug, and info logs for
      tracking program behavior.
    - `csv_utils.py`: Utility functions to:
        - Merge or append CSV files.
        - Back up old CSV files (e.g., creating `transactions_history_previous.csv`).

---

#### **`tests/` (Unit Tests Directory)**

This directory contains unit tests for the core modules:

- `test_file_handler.py`: Ensures the file-handling functions work as expected, including locating and validating
  database files.
- `test_transaction_exporter.py`: Verifies the functionality of exporting data to CSVs.
- `test_db_handler.py`: Tests database-related functions, including SQL query execution and validation.

---

## Usage

### Command-Line Execution

Run the program using the following command:

```bash
python main.py <db_directory>
```

- `<db_directory>`: The path to the directory containing the database files. If absent, the application uses the current
  directory by default.

---

### Example:

1. Assume your SQLite database files (`cashew_*.sql`) are in a folder called `/data/dbs/`.
2. Run this command:

   ```bash
   python main.py /data/dbs/
   ```

3. The application will:
    - Locate the most recent file with the prefix `cashew` and the `.sql` extension.
    - Export the transaction data to the following CSV files in the same directory:
        - `transactions.csv`
        - `transactions_history_previous.csv`
        - `transactions_history.csv`

---

## Getting Started

### Requirements

- **Python Version**: Python 3.10 or newer
- **Dependencies**: Install the required libraries with `pip`:

   ```bash
   pip install -r requirements.txt
   ```

---

### Setup

1. Clone the repository:

   ```bash
   git clone <repository_url>
   ```

2. Navigate to the directory:

   ```bash
   cd transaction_exporter
   ```

3. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the program via the [Usage](#usage) instructions.

---

## Notes

- Ensure database files conform to the naming convention (`<DB_FILE_PREFIX>_<timestamp>.<DB_FILE_SUFFIX>`), where:
    - `DB_FILE_PREFIX`: Default prefix is `cashew`.
    - `DB_FILE_SUFFIX`: File extension, typically `.sql`.
- All output files (`transactions.csv`, etc.) are placed in the same directory as the database files.

---
