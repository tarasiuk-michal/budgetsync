from src.csv_handler import CSVHandler

def test_read_existing_csv(test_csv):
    """Test reading an existing CSV file."""
    # Write test data to fake CSV
    headers = ['id', 'opis', 'kwota', 'kategoria', 'data']
    rows = [
        ['1', 'Groceries', '50,00', 'spożywcze', '01.01.2023'],
        ['2', 'Bus Ticket', '2,50', 'transport', '02.01.2023']
    ]
    with open(test_csv, 'w', encoding='utf-8') as f:
        f.write(";".join(headers) + "\n")
        for row in rows:
            f.write(";".join(row) + "\n")

    data = CSVHandler.read_existing_csv(test_csv)
    assert len(data) == 2
    assert tuple(rows[0]) in data  # Ensure the first row exists in the results


def test_write_to_csv(test_csv):
    """Test writing data to a CSV file."""
    headers = ['id', 'opis', 'kwota', 'kategoria', 'data']
    rows = [
        ['1', 'Groceries', '50,00', 'spożywcze', '01.01.2023'],
        ['2', 'Bus Ticket', '2,50', 'transport', '02.01.2023']
    ]
    CSVHandler.write_to_csv(test_csv, headers, rows)

    # Read the file back and check its contents
    with open(test_csv, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    assert lines[0].strip() == ";".join(headers)
    assert lines[1].strip() == ";".join(rows[0])
    assert lines[2].strip() == ";".join(rows[1])