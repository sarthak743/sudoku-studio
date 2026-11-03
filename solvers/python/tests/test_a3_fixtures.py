import json
import time
from pathlib import Path

import pytest
from sudoku_solvers.a1 import SearchTimeout
from sudoku_solvers.a3 import solve_a3
from sudoku_solvers.parser import parse_grid, serialize_grid, validate_format
from sudoku_solvers.validator import classify_completed_grid, validate_board

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "data" / "puzzles" / "edge_cases.json"

with FIXTURE_PATH.open(encoding="utf-8") as file:
    FIXTURES = json.load(file)


A3_FIXTURES = [
    fixture for fixture in FIXTURES if "algorithms" not in fixture or "A3" in fixture["algorithms"]
]


@pytest.mark.parametrize(
    "fixture",
    A3_FIXTURES,
    ids=lambda fixture: fixture["id"],
)
def test_a3_against_edge_cases(fixture):
    grid = fixture["grid"]

    expected = fixture.get("expected_by_algorithm", {}).get(
        "A3",
        fixture,
    )

    try:
        validate_format(grid)
        board = parse_grid(grid)
    except ValueError:
        assert expected["expected_status"] == "invalid_format"
        return

    if validate_board(board):
        assert expected["expected_status"] == "invalid"
        return

    if classify_completed_grid(board) == "already_solved":
        assert expected["expected_status"] == "already_solved"
        return

    solutions = []
    solution_count = 0
    nodes = [0]
    backtracks = [0]
    timed_out = False

    deadline = time.monotonic() + fixture.get("deadline_ms", 10_000) / 1000

    try:
        for solution in solve_a3(
            board,
            deadline=deadline,
            node_counter=nodes,
            backtrack_counter=backtracks,
        ):
            solution_count += 1

            if len(solutions) < 15:
                solutions.append(serialize_grid(solution))

    except SearchTimeout:
        timed_out = True

    if timed_out and solution_count < 2:
        status = "timeout"
    elif solution_count == 0:
        status = "unsolvable"
    elif solution_count == 1:
        status = "unique"
    else:
        status = "multiple"

    assert status == expected["expected_status"]

    count_type = expected["count_type"]
    expected_count = expected["expected_solution_count"]

    if count_type == "exact":
        assert solution_count == expected_count

    elif count_type == "lower_bound":
        assert solution_count >= expected_count

    elif count_type == "not_applicable":
        assert solution_count == 0

    assert len(solutions) <= 15
    assert nodes[0] >= 0
    assert backtracks[0] >= 0
