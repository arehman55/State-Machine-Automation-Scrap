from pathlib import Path

import pytest

from src.security import encrypt_excel_with_password


def test_encrypt_excel_file_not_found():
    """Test that FileNotFoundError is raised if the source Excel file is missing."""
    invalid_path = Path("does_not_exist.xlsx")

    with pytest.raises(FileNotFoundError):
        encrypt_excel_with_password(invalid_path, "Secret123")
