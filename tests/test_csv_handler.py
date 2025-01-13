from src.csv_handler import CSVHandler


def test_read_existing_csv(test_csv):
    """Test reading an existing CSV file."""
    headers = ['id', 'opis', 'kwota', 'kategoria', 'data']
    rows = [['1', 'Groceries', '50,00', 'spożywcze', '01.01.2023'],
            ['2', 'Bus Ticket', '2,50', 'transport', '02.01.2023']]
    with open(test_csv, 'w', encoding='utf-8') as f:
        f.write(";".join(headers) + "\n")
        for row in rows:
            f.write(";".join(row) + "\n")

    # Call with correct static method signature
    data = CSVHandler.read_existing_csv(test_csv)

    assert data == {
        ('1', 'Groceries', '50,00', 'spożywcze', '01.01.2023'),
        ('2', 'Bus Ticket', '2,50', 'transport', '02.01.2023'),
    }


def test_write_to_csv(test_csv):
    """Test writing data to a CSV file."""
    headers = ['id', 'opis', 'kwota', 'kategoria', 'data']
    rows = [['1', 'Groceries', '50,00', 'spożywcze', '01.01.2023'],
            ['2', 'Bus Ticket', '2,50', 'transport', '02.01.2023']]

    # Call with correct static method signature
    CSVHandler.write_to_csv(test_csv, headers, rows)

    with open(test_csv, 'r', encoding='utf-8') as f:
        lines = f.read().strip().split("\n")
        assert lines[0] == ";".join(headers)
        assert lines[1:] == [";".join(row) for row in rows]
