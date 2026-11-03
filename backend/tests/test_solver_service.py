
from app.schemas.common import SolverStatus
from app.services.solver_service import (
    solve_with_algorithm,
    solve_with_all_algorithms,
)


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


def test_solve_with_a1():
    result = solve_with_algorithm(VALID_GRID, "A1")

    assert result.status == SolverStatus.UNIQUE
    assert result.solution_count == 1
    assert len(result.solutions) == 1
    assert result.algorithm == "A1"


def test_solve_with_all_algorithms():
    result = solve_with_all_algorithms(VALID_GRID)

    assert len(result.algorithm_results) == 4
    assert result.selected_result.status == SolverStatus.UNIQUE

    assert {
        item.algorithm for item in result.algorithm_results
    } == {"A1", "A2", "A3", "A4"}


def test_all_algorithms_return_same_solution():
    result = solve_with_all_algorithms(VALID_GRID)

    solutions = [
        item.solution_count
        for item in result.algorithm_results
    ]

    assert solutions == [1, 1, 1, 1]


def test_already_solved_grid():
    solved = (
        "534678912"
        "672195348"
        "198342567"
        "859761423"
        "426853791"
        "713924856"
        "961537284"
        "287419635"
        "345286179"
    )

    result = solve_with_algorithm(solved, "A2")

    assert result.status == SolverStatus.ALREADY_SOLVED
    assert result.solution_count == 1


def test_invalid_grid():
    invalid = (
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

    result = solve_with_algorithm(invalid, "A3")

    assert result.status == SolverStatus.INVALID
    assert result.solution_count == 0



import pytest


MULTIPLE_SOLUTION_GRID = (
    "530070000"
    "600195000"
    "098000060"
    "000000003"
    "400803001"
    "700020006"
    "060000280"
    "000409005"
    "000000079"
)


@pytest.mark.parametrize("algorithm", ["A1", "A2", "A3", "A4"])
def test_multiple_solution_enumeration(algorithm):
    result = solve_with_algorithm(
        MULTIPLE_SOLUTION_GRID,
        algorithm,
    )

    assert result.status == SolverStatus.MULTIPLE
    assert result.solution_count == 16
    assert len(result.solutions) == 15
    assert result.count_capped is False
    assert result.timed_out is False



from app.services.solver_service import solve_with_algorithm
from sudoku_solvers.a1 import SearchTimeout


SOLVED_GRID = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)

EMPTY_GRID = "0" * 81


def test_timeout_before_first_solution(monkeypatch):
    def interrupted_solver(*args, **kwargs):
        raise SearchTimeout
        yield

    monkeypatch.setattr(
        "app.services.solver_service.get_algorithm",
        lambda algorithm: interrupted_solver,
    )

    result = solve_with_algorithm(EMPTY_GRID, "A1")

    assert result.status == SolverStatus.TIMEOUT
    assert result.solution_count == 0
    assert result.solutions == []
    assert result.timed_out is True


def test_timeout_after_exactly_one_solution(monkeypatch):
    def interrupted_solver(*args, **kwargs):
        yield [list(SOLVED_GRID[i:i + 9]) for i in range(0, 81, 9)]
        raise SearchTimeout

    monkeypatch.setattr(
        "app.services.solver_service.get_algorithm",
        lambda algorithm: interrupted_solver,
    )

    result = solve_with_algorithm(EMPTY_GRID, "A1")

    assert result.status == SolverStatus.TIMEOUT
    assert result.solution_count == 1
    assert len(result.solutions) == 1
    assert result.timed_out is True


def test_timeout_after_multiple_solutions(monkeypatch):
    def interrupted_solver(*args, **kwargs):
        solution = [
            list(SOLVED_GRID[i:i + 9])
            for i in range(0, 81, 9)
        ]

        yield solution
        yield solution
        raise SearchTimeout

    monkeypatch.setattr(
        "app.services.solver_service.get_algorithm",
        lambda algorithm: interrupted_solver,
    )

    result = solve_with_algorithm(EMPTY_GRID, "A1")

    assert result.status == SolverStatus.MULTIPLE
    assert result.solution_count == 2
    assert result.timed_out is True
