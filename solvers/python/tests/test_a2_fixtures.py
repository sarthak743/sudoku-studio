import json
import time
from pathlib import Path

import pytest
from sudoku_solvers.a1 import SearchTimeout
from sudoku_solvers.a2 import solve_a2
from sudoku_solvers.parser import parse_grid, serialize_grid, validate_format
from sudoku_solvers.validator import (
    classify_completed_grid,
    validate_board,
)

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "data" / "puzzles" / "edge_cases.json"

with FIXTURE_PATH.open(encoding="utf-8") as file:
    FIXTURES = json.load(file)


A2_FIXTURES = [
    fixture for fixture in FIXTURES if "algorithms" not in fixture or "A2" in fixture["algorithms"]
]


@pytest.mark.parametrize(
    "fixture",
    A2_FIXTURES,
    ids=lambda fixture: fixture["id"],
)
def test_a2_against_edge_cases(fixture):
    grid = fixture["grid"]

    try:
        validate_format(grid)
        board = parse_grid(grid)
    except ValueError:
        assert fixture["expected_status"] == "invalid_format"
        return

    if validate_board(board):
        assert fixture["expected_status"] == "invalid"
        return

    if classify_completed_grid(board) == "already_solved":
        assert fixture["expected_status"] == "already_solved"
        return

    solutions = []
    solution_count = 0
    nodes = [0]
    backtracks = [0]
    timed_out = False

    deadline = time.monotonic() + fixture.get("deadline_ms", 10_000) / 1000

    try:
        for solution in solve_a2(
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

    assert status == fixture["expected_status"]

    count_type = fixture["count_type"]
    expected_count = fixture["expected_solution_count"]

    if count_type == "exact":
        assert solution_count == expected_count

    elif count_type == "lower_bound":
        assert solution_count >= expected_count

    elif count_type == "not_applicable":
        assert solution_count == 0

    assert len(solutions) <= 15
    assert nodes[0] >= 0
    assert backtracks[0] >= 0
