
import pytest

from app.services.validation_service import validate_sudoku


VALID_GRID = (
    "530070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079"
)


def test_valid_grid():
    result = validate_sudoku(VALID_GRID)

    assert result.valid is True
    assert result.conflicts == []


def test_duplicate_row():
    grid = (
        "550070000"
        "600195000"
        "098000060"
        "800060003"
        "400803001"
        "700020006"
        "060000280"
        "000419005"
        "000080079"
    )

    result = validate_sudoku(grid)

    assert result.valid is False
    assert len(result.conflicts) > 0


def test_duplicate_column():
    grid = (
        "530070000"
        "500195000"
        "098000060"
        "800060003"
        "400803001"
        "700020006"
        "060000280"
        "000419005"
        "000080079"
    )

    result = validate_sudoku(grid)

    assert result.valid is False
    assert len(result.conflicts) > 0


def test_duplicate_box():
    grid = (
        "530070000"
        "600195000"
        "098000060"
        "800060003"
        "400803001"
        "700020006"
        "060000280"
        "000419005"
        "000080079"
    )

    result = validate_sudoku(grid)

    assert result.valid is True


@pytest.mark.parametrize(
    "grid",
    [
        "123",
        "x" * 81,
        "1" * 82,
    ],
)
def test_invalid_grid_format(grid):
    with pytest.raises(ValueError):
        validate_sudoku(grid)
