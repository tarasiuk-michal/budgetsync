import os
import pytest


def test_main_script(test_db, test_csv):
    """Test the main script execution."""
    from src.main import main
    import sys

    # Override sys.argv with fake arguments
    sys.argv = ['main.py', str(test_db), str(test_csv)]

    try:
        main()
        assert os.path.exists(test_csv)  # Ensure the output CSV was created
    except Exception as e:
        pytest.fail(f"Main script failed: {e}")