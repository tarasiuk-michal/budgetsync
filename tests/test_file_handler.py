import re
from unittest.mock import patch, mock_open, call

from config import SQL_FILE_NAME_REGEX
from src.handlers.file_handler import FileHandler


def test_find_latest_sql_file(tmp_path):
    # Create mock files in the pytest temp directory
    invalid_file = tmp_path / "invalid_file.sql"
    valid_old_file = tmp_path / "cashew-db-v7-X55 minor update 2023-10-01-01-02-59-123Z.sql"
    valid_new_file = tmp_path / "cashew-db-v1-X23 update migration 2023-10-04-14-30-59-123Z.sql"

    # Create the files
    invalid_file.touch()
    valid_old_file.touch()
    valid_new_file.touch()

    # Call the function under test with the tmp_path
    result = FileHandler.find_latest_sql_file(str(tmp_path))

    # Assert the result is the valid file
    assert result == str(valid_new_file)


def test_find_latest_pixel_sql_file(tmp_path):
    # Create mock files in the pytest temp directory
    invalid_file = tmp_path / "invalid_file.sql"
    valid_old_file = tmp_path / "cashew-sync-Pixel 6 Pro-17119321369862025-02-04-04-10-01-397Z.sql"
    valid_new_file = tmp_path / "cashew-sync-Pixel 6 Pro-17119321369862025-02-04-04-17-01-397Z.sql"

    # Create the files
    invalid_file.touch()
    valid_old_file.touch()
    valid_new_file.touch()

    # Call the function under test with the tmp_path
    result = FileHandler.find_latest_sql_file(str(tmp_path))

    # Assert the result is the valid file
    assert result == str(valid_new_file)


def test_regex_match_filenames():
    # Test filenames
    test_filenames = [
        "cashew-sync-Pixel 6 Pro-17119321369862025-02-04-04-17-01-397Z.sql",
        "cashew-db-v1-X12345-RandomStuff-2025-02-04-04-17-01-397Z.sql",
        "cashew-arbitrary-in-middle-2025-02-04-04-17-01-397Z.sql",
        "random-cashew-prefix-2025-02-04-04-17-01-397Z.sql",  # Shouldn't match; doesn't begin with "cashew"
        "cashew-file-invalid.sql",  # Shouldn't match; no timestamp
    ]

    for filename in test_filenames:
        if re.match(SQL_FILE_NAME_REGEX, filename):
            print(f"Matched: {filename}")
        else:
            print(f"Did not match: {filename}")


@patch('builtins.open', new_callable=mock_open)
def test_write_to_file(mock_file):
    FileHandler.write_to_file("test.csv", [["col1", "col2"], ["data1", "data2"]])

    # Verify the content written in the correct sequence
    expected_calls = [
        # Expect 'col1' and 'col2' to be written first
        call().write("col1\tcol2\r\n"),
        # Then 'data1' and 'data2' to be written
        call().write("data1\tdata2\r\n"),
    ]

    # Assert the sequence of calls was made
    mock_file.assert_has_calls(expected_calls, any_order=False)
