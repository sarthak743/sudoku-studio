import pytest
from sudoku_solvers.parser import (
    parse_grid,
    serialize_grid,
    validate_format,
)


def test_parse_grid_returns_9x9_board():
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

    board = parse_grid(grid)

    assert len(board) == 9
    assert all(len(row) == 9 for row in board)


def test_parse_grid_normalizes_zero_to_dot():
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

    board = parse_grid(grid)

    assert board[0] == ["5", "3", ".", ".", "7", ".", ".", ".", "."]


def test_validate_format_rejects_wrong_length():
    with pytest.raises(ValueError):
        validate_format("12345")


def test_validate_format_rejects_invalid_character():
    grid = "x" + "0" * 80

    with pytest.raises(ValueError):
        validate_format(grid)


def test_validate_format_rejects_non_string():
    with pytest.raises(ValueError):
        validate_format(None)


def test_serialize_grid_returns_81_characters():
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

    board = parse_grid(grid)

    assert serialize_grid(board) == grid.replace("0", ".")


def test_serialize_grid_rejects_invalid_dimensions():
    with pytest.raises(ValueError):
        serialize_grid([["."] * 8 for _ in range(9)])
