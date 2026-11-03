import time

import pytest
from sudoku_solvers.a1 import SearchTimeout
from sudoku_solvers.a2 import solve_a2
from sudoku_solvers.parser import parse_grid, serialize_grid


def test_a2_solves_valid_puzzle():
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

    board = parse_grid(grid)
    original = serialize_grid(board)

    solutions = list(solve_a2(board))

    assert len(solutions) == 1
    assert serialize_grid(solutions[0]) == (
        "534678912672195348198342567859761423426853791713924856961537284287419635345286179"
    )
    assert serialize_grid(board) == original


def test_a2_finds_multiple_solutions():
    grid = "530070000600195000098000000800060003400803001700020006060000280000419005000080079"

    board = parse_grid(grid)
    solutions = []

    for solution in solve_a2(board):
        solutions.append(solution)

        if len(solutions) == 2:
            break

    assert len(solutions) == 2


def test_a2_returns_search_metrics():
    board = parse_grid(
        "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
    )

    nodes = [0]
    backtracks = [0]

    list(
        solve_a2(
            board,
            node_counter=nodes,
            backtrack_counter=backtracks,
        )
    )

    assert nodes[0] > 0
    assert backtracks[0] >= 0


def test_a2_preserves_original_board():
    board = [
        list("53..7...."),
        list("6..195..."),
        list(".98....6."),
        list("8...6...3"),
        list("4..8.3..1"),
        list("7...2...6"),
        list(".6....28."),
        list("...419..5"),
        list("....8..79"),
    ]

    original = [row[:] for row in board]

    list(solve_a2(board))

    assert board == original


def test_a2_is_repeatable_on_same_board():
    board = [
        list("53..7...."),
        list("6..195..."),
        list(".98....6."),
        list("8...6...3"),
        list("4..8.3..1"),
        list("7...2...6"),
        list(".6....28."),
        list("...419..5"),
        list("....8..79"),
    ]

    first_run = list(solve_a2(board))
    second_run = list(solve_a2(board))

    assert first_run == second_run


def test_a2_handles_timeout():
    board = [list("." * 9) for _ in range(9)]

    with pytest.raises(SearchTimeout):
        list(solve_a2(board, deadline=time.monotonic() - 1))


def test_a2_restores_board_after_timeout():
    board = [list("." * 9) for _ in range(9)]
    original = [row[:] for row in board]

    with pytest.raises(SearchTimeout):
        list(solve_a2(board, deadline=time.monotonic() - 1))

    assert board == original


def test_a2_can_solve_after_previous_timeout():
    board = [
        list("53..7...."),
        list("6..195..."),
        list(".98....6."),
        list("8...6...3"),
        list("4..8.3..1"),
        list("7...2...6"),
        list(".6....28."),
        list("...419..5"),
        list("....8..79"),
    ]

    with pytest.raises(SearchTimeout):
        list(solve_a2(board, deadline=time.monotonic() - 1))

    solutions = list(solve_a2(board))

    assert len(solutions) == 1


def test_a2_solutions_are_valid():
    from sudoku_solvers.validator import validate_board

    board = [
        list("53..7...."),
        list("6..195..."),
        list(".98....6."),
        list("8...6...3"),
        list("4..8.3..1"),
        list("7...2...6"),
        list(".6....28."),
        list("...419..5"),
        list("....8..79"),
    ]

    solutions = list(solve_a2(board))

    assert solutions

    for solution in solutions:
        assert not validate_board(solution)
        for row in range(9):
            for col in range(9):
                if board[row][col] != ".":
                    assert solution[row][col] == board[row][col]


def test_a2_handles_unsolvable_puzzle():
    from sudoku_solvers.a2 import solve_a2

    board = [
        list("12345678."),
        list("........9"),
        *[list(".........") for _ in range(7)],
    ]

    solutions = list(solve_a2(board))

    assert solutions == []


def test_a2_restores_masks_after_failed_branches():
    board = [
        list("53..7...."),
        list("6..195..."),
        list(".98....6."),
        list("8...6...3"),
        list("4..8.3..1"),
        list("7...2...6"),
        list(".6....28."),
        list("...419..5"),
        list("....8..79"),
    ]

    original = [row[:] for row in board]

    first_run = list(solve_a2(board))
    second_run = list(solve_a2(board))

    assert first_run
    assert first_run == second_run
    assert board == original
