# budgetsync

budgetsync is a lightweight tool designed to help individuals and organizations manage their financial budgets
effectively. This application allows you to track income, expenses, and generate meaningful insights to better visualize
and plan your finances.
---

## Project Structure

The project directory is organized as follows:

```
budgetsync/
├── src/                    # Source code for the application
│   ├── main.py             # Entry point of the application
│   ├── budget_manager.py   # Contains logic for handling budgets
│   ├── data_manager.py     # Handles data persistence and storage
│   └── utils/              # Utility functions and helpers
│       ├── formatter.py    # Formatting tools for reports
│       └── calculator.py   # Financial calculations logic
├── tests/                  # Unit and integration tests
│   ├── test_budget_manager.py
│   ├── test_data_manager.py
│   └── test_calculator.py
├── requirements.txt        # Python dependencies for the project
├── .gitignore              # Files and directories to ignore in git
└── README.md               # Project documentation (this file)
```

---

## Features

- Add, edit, or delete income and expense items.
- View budget summaries and reports.
- Export financial data for analysis.
- Supports multiple users with independent data storage.

---

## Usage

1. Launch the application using the command above.
2. Select from the menu options to perform various budget management tasks:
    - Add income/expense transactions.
    - View budget summaries.
    - Export reports.
      Instructions and prompts will guide you through the process.

---

## Running Tests

To run the tests, execute the following command from the project directory:

```bash
pytest tests/
```


## Contact

If you have any questions or issues, feel free to reach out:

- [GitHub](https://github.com/tarasiuk-michal/budgetsync)
