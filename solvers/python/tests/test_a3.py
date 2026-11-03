import time

import pytest
from sudoku_solvers.a1 import SearchTimeout
from sudoku_solvers.a3 import solve_a3
from sudoku_solvers.validator import validate_board


def test_a3_solves_valid_puzzle():
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

    solutions = list(solve_a3(board))

    assert len(solutions) == 1
    assert solutions[0][0] == list("534678912")


def test_a3_preserves_original_board():
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

    list(solve_a3(board))

    assert board == original


def test_a3_finds_multiple_solutions():
    board = [list("." * 9) for _ in range(9)]

    solutions = []

    for solution in solve_a3(board):
        solutions.append(solution)

        if len(solutions) == 2:
            break

    assert len(solutions) == 2


def test_a3_returns_search_metrics():
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

    nodes = [0]
    backtracks = [0]

    list(
        solve_a3(
            board,
            node_counter=nodes,
            backtrack_counter=backtracks,
        )
    )

    assert nodes[0] > 0
    assert backtracks[0] >= 0


def test_a3_is_repeatable():
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

    first = list(solve_a3(board))
    second = list(solve_a3(board))

    assert first == second


def test_a3_handles_timeout():
    board = [list("." * 9) for _ in range(9)]

    with pytest.raises(SearchTimeout):
        list(solve_a3(board, deadline=time.monotonic() - 1))


def test_a3_restores_board_after_timeout():
    board = [list("." * 9) for _ in range(9)]
    original = [row[:] for row in board]

    with pytest.raises(SearchTimeout):
        list(solve_a3(board, deadline=time.monotonic() - 1))

    assert board == original


def test_a3_can_solve_after_previous_timeout():
    board = [list("." * 9) for _ in range(9)]
    original = [row[:] for row in board]

    with pytest.raises(SearchTimeout):
        list(solve_a3(board, deadline=time.monotonic() - 1))

    assert board == original

    # Run again with a normal deadline.
    solutions = []

    for solution in solve_a3(board):
        solutions.append(solution)

        if len(solutions) == 1:
            break

    assert len(solutions) == 1
    assert board == original


def test_a3_solutions_are_valid():
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

    solutions = list(solve_a3(board))

    assert solutions

    for solution in solutions:
        assert not validate_board(solution)

        for row in range(9):
            for col in range(9):
                if board[row][col] != ".":
                    assert solution[row][col] == board[row][col]


def test_a3_handles_unsolvable_puzzle():
    board = [
        list("12345678."),
        list("........9"),
        *[list(".........") for _ in range(7)],
    ]

    solutions = list(solve_a3(board))

    assert solutions == []


def test_a3_is_repeatable_after_backtracking():
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

    first = list(solve_a3(board))
    second = list(solve_a3(board))

    assert first == second
    assert board == original
