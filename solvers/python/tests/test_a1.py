from sudoku_solvers.a1 import solve_a1
from sudoku_solvers.parser import parse_grid


def test_a1_solves_valid_puzzle():
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

    solutions = list(solve_a1(parse_grid(grid)))

    assert len(solutions) == 1
    assert all("." not in row for row in solutions[0])


def test_a1_preserves_original_board():
    board = parse_grid(
        "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
    )
    original = [row[:] for row in board]

    list(solve_a1(board))

    assert board == original


def test_a1_finds_multiple_solutions():
    board = parse_grid(
        "100000000000000000000000000000000000000000000000000000000000000000000000000000000"
    )

    solutions = []
    for solution in solve_a1(board):
        solutions.append(solution)
        if len(solutions) == 2:
            break

    assert len(solutions) == 2
