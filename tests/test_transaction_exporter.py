import pytest
from src.transaction_exporter import TransactionExporter

@pytest.fixture
def exporter(test_db, test_csv):
    """Fixture to create a TransactionExporter instance."""
    return TransactionExporter(str(test_db), str(test_csv))


def test_process_rows(exporter):
    """Test processing of rows into the correct format."""
    rows = [
        (1, 'Groceries', 50.00, '2', 1672531200),  # Valid data
        (4, 'Unknown', 25.00, '999', 1672790400),  # Invalid category
    ]
    processed = exporter.process_rows(rows)

    assert len(processed) == 2
    assert processed[0] == ['1', '50,00', '01.01.2023', 'Groceries', 'spożywcze']
    assert processed[1][4] == 'inne'  # Check default category for unknown


def test_fetch_and_export(exporter):
    """Test the end-to-end fetching and exporting process."""
    exporter.fetch_and_export()

    # Read the CSV and validate its contents
    with open(exporter.output_csv, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    assert len(lines) > 1  # Header + Data
    assert '1;50,00;01.01.2023;Groceries;spożywcze' in lines[1]