"""
Unit tests for coordinate and target input validation.
"""

import pytest
from fastapi import HTTPException

from backend.utils.validation import sanitize_target_name, validate_coordinates


def test_valid_coordinates():
    ra, dec, rad = validate_coordinates(133.795, -7.245, 3.0)
    assert ra == 133.795
    assert dec == -7.245
    assert rad == 3.0


def test_invalid_ra_out_of_bounds():
    with pytest.raises(HTTPException) as excinfo:
        validate_coordinates(400.0, 10.0)
    assert excinfo.value.status_code == 400
    assert "out of bounds" in excinfo.value.detail


def test_invalid_dec_out_of_bounds():
    with pytest.raises(HTTPException) as excinfo:
        validate_coordinates(100.0, -95.0)
    assert excinfo.value.status_code == 400
    assert "out of bounds" in excinfo.value.detail


def test_invalid_radius():
    with pytest.raises(HTTPException) as excinfo:
        validate_coordinates(100.0, 10.0, -1.0)
    assert excinfo.value.status_code == 400

    with pytest.raises(HTTPException) as excinfo:
        validate_coordinates(100.0, 10.0, 100.0)
    assert excinfo.value.status_code == 400


def test_sanitize_target_name_valid():
    assert sanitize_target_name("WISE 0855-0714") == "WISE 0855-0714"
    assert sanitize_target_name("Barnard's Star") == "Barnard's Star" or "Barnard" in sanitize_target_name("Barnard's Star")


def test_sanitize_target_name_injection_rejection():
    with pytest.raises(HTTPException) as excinfo:
        sanitize_target_name("target; DROP TABLE users;--")
    assert excinfo.value.status_code == 400

