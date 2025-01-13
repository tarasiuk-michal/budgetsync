import src.file_handler


def test_process_rows(exporter):
    """Test processing of rows into the correct format."""
    rows = [
        (1, 'Groceries', 50.00, '2', 1672531200),  # Valid data
        (4, 'Unknown', 25.00, '999', 1672790400),  # Invalid category
    ]
    processed = exporter.process_rows(rows)

    assert len(processed) == 2
    assert processed[0] == [1, '50,00', '01.01.2023', 'Groceries', 'spożywcze']
    assert processed[1][4] == 'inne'  # Check default category for unknown


def test_fetch_and_export(mocker, exporter):
    """Test the end-to-end fetching and exporting process."""
    # Mock fetch_transactions to return dummy transaction data
    mocker.patch(
        'src.db_handler.DBHandler.fetch_transactions',
        return_value=[
            (1, 'Groceries', 50.00, '2', 1672531200),  # Dummy data
            (2, 'Fuel', 30.00, '3', 1672617600)  # Additional row
        ]
    )

    # Mock read_existing_csv to simulate no existing data
    mocker.patch(
        'src.csv_handler.CSVHandler.read_existing_csv',
        return_value=set()  # Simulate an empty CSV file
    )

    # Call the method to fetch and export
    exporter.fetch_and_export()

    # Open the CSV file and assert its contents
    with open(exporter.output_csv, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Check if file writing occurred and content validity
    assert len(lines) > 1  # Includes headers + data rows
    assert '1;50,00;01.01.2023;Groceries;spożywcze' in lines[1]
    assert '2;30,00;02.01.2023;Fuel;' in lines[2]  # Ensure the second entry exists


def test_output_to_multiple_files(mocker, exporter):
    """Test output to history, backup, and new records files."""
    rows = [
        (1, 'Groceries', 50.00, '2', 1672531200),
        (2, 'Fuel', 30.00, '3', 1672617600)
    ]

    # Mock component interactions
    mocker.patch(
        'src.file_handler.FileHandler.write_to_file',
        side_effect=[None, None, None]
    )

    exporter.output_files(rows)

    # Verify each file is written
    history_output = f"{exporter.output_csv}_history.csv"
    backup_output = f"{exporter.output_csv}_backup.csv"
    new_records_output = f"{exporter.output_csv}_new.csv"

    mocker.patch.object(src.file_handler.FileHandler, 'write_to_file').assert_any_call(history_output, rows)
    mocker.patch.object(src.file_handler.FileHandler, 'write_to_file').assert_any_call(backup_output, rows)
    mocker.patch.object(src.file_handler.FileHandler, 'write_to_file').assert_any_call(new_records_output, rows)
