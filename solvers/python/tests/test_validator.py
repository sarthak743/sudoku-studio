import json
from pathlib import Path

import pytest
from sudoku_solvers.parser import parse_grid
from sudoku_solvers.validator import (
    classify_completed_grid,
    find_box_conflicts,
    find_column_conflicts,
    find_row_conflicts,
    validate_board,
    validate_input,
)

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "data" / "puzzles" / "edge_cases.json"


def test_row_without_duplicates():
    board = [["."] * 9 for _ in range(9)]
    board[0] = list("123456789")

    assert find_row_conflicts(board) == []


def test_row_with_one_duplicate():
    board = [["."] * 9 for _ in range(9)]
    board[0] = list("123456781")

    assert find_row_conflicts(board) == [(0, 0), (0, 8)]


def test_row_with_multiple_duplicates():
    board = [["."] * 9 for _ in range(9)]
    board[0] = list("112233...")

    assert find_row_conflicts(board) == [
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
    ]


def test_empty_cells_are_ignored():
    board = [["."] * 9 for _ in range(9)]

    assert find_row_conflicts(board) == []


def test_column_without_duplicates():
    board = [["."] * 9 for _ in range(9)]

    for row in range(9):
        board[row][0] = str(row + 1)

    assert find_column_conflicts(board) == []


def test_column_with_one_duplicate():
    board = [["."] * 9 for _ in range(9)]
    board[0][0] = "5"
    board[4][0] = "5"

    assert find_column_conflicts(board) == [(0, 0), (4, 0)]


def test_column_with_multiple_duplicates():
    board = [["."] * 9 for _ in range(9)]
    board[0][0] = "1"
    board[1][0] = "1"
    board[2][0] = "2"
    board[3][0] = "2"

    assert find_column_conflicts(board) == [
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 0),
    ]


def test_empty_cells_are_ignored_in_column():
    board = [["."] * 9 for _ in range(9)]

    assert find_column_conflicts(board) == []


def test_box_without_duplicates():
    board = [["."] * 9 for _ in range(9)]
    board[0][0] = "1"
    board[0][1] = "2"
    board[0][2] = "3"
    board[1][0] = "4"
    board[1][1] = "5"
    board[1][2] = "6"
    board[2][0] = "7"
    board[2][1] = "8"
    board[2][2] = "9"

    assert find_box_conflicts(board) == []


def test_box_with_one_duplicate():
    board = [["."] * 9 for _ in range(9)]
    board[0][0] = "5"
    board[2][2] = "5"

    assert find_box_conflicts(board) == [(0, 0), (2, 2)]


def test_box_with_multiple_duplicates():
    board = [["."] * 9 for _ in range(9)]
    board[0][0] = "1"
    board[1][1] = "1"
    board[0][2] = "2"
    board[2][0] = "2"

    assert find_box_conflicts(board) == [(0, 0), (0, 2), (1, 1), (2, 0)]


def test_empty_cells_are_ignored_in_box():
    board = [["."] * 9 for _ in range(9)]

    assert find_box_conflicts(board) == []


def test_validate_board_valid_puzzle():
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
    board = parse_grid(grid)

    assert validate_board(board) == []


def test_validate_board_detects_conflicts():
    board = [["."] * 9 for _ in range(9)]
    board[0][0] = "5"
    board[0][1] = "5"

    assert validate_board(board) == [(0, 0), (0, 1)]


def test_invalid_fixtures_are_detected():
    fixtures = json.loads(FIXTURE_PATH.read_text())

    for fixture in fixtures:
        if fixture["expected_status"] != "invalid":
            continue

        board = parse_grid(fixture["grid"])
        assert validate_board(board), fixture["id"]


def test_valid_and_solvable_fixtures_have_no_conflicts():
    fixtures = json.loads(FIXTURE_PATH.read_text())

    expected_valid = {"unique", "multiple", "already_solved", "unsolvable"}

    for fixture in fixtures:
        if fixture["expected_status"] not in expected_valid:
            continue

        board = parse_grid(fixture["grid"])
        assert validate_board(board) == [], fixture["id"]


def test_validate_input_accepts_valid_grid():
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

    assert validate_input(grid) == []


def test_validate_input_rejects_duplicate_givens():
    grid = "550070000600195000098000060800060003400803001700020006060000280000419005000080079"

    assert validate_input(grid)


def test_validate_input_rejects_malformed_grid():
    with pytest.raises(ValueError):
        validate_input("12345")


def test_classify_completed_valid_grid():
    board = parse_grid(
        "534678912672195348198342567859761423426853791713924856961537284287419635345286179"
    )
    assert classify_completed_grid(board) == "already_solved"


def test_classify_completed_invalid_grid():
    board = parse_grid(
        "554678912672195348198342567859761423426853791713924856961537284287419635345286179"
    )
    assert classify_completed_grid(board) == "invalid"


def test_classify_incomplete_grid():
    board = parse_grid(
        "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
    )
    assert classify_completed_grid(board) == "incomplete"
