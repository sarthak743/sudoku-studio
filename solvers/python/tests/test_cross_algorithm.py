import json
import time
from pathlib import Path

import pytest
from sudoku_solvers.a1 import SearchTimeout, solve_a1
from sudoku_solvers.a2 import solve_a2
from sudoku_solvers.a3 import solve_a3
from sudoku_solvers.a4 import solve_a4
from sudoku_solvers.parser import parse_grid, serialize_grid, validate_format
from sudoku_solvers.validator import (
    classify_completed_grid,
    validate_board,
)

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "data" / "puzzles" / "edge_cases.json"

with FIXTURE_PATH.open(encoding="utf-8") as file:
    FIXTURES = json.load(file)


ALGORITHMS = {
    "A1": solve_a1,
    "A2": solve_a2,
    "A3": solve_a3,
    "A4": solve_a4,
}


@pytest.mark.parametrize(
    "fixture",
    FIXTURES,
    ids=lambda fixture: fixture["id"],
)
def test_cross_algorithm_consistency(fixture):
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

    results = {}

    for algorithm_id, solve_function in ALGORITHMS.items():
        expected = fixture.get("expected_by_algorithm", {}).get(
            algorithm_id,
            fixture,
        )

        if "algorithms" in fixture and algorithm_id not in fixture["algorithms"]:
            continue

        algorithm_board = [row[:] for row in board]
        original_board = [row[:] for row in algorithm_board]

        solutions = []
        solution_count = 0
        nodes = [0]
        backtracks = [0]
        timed_out = False

        deadline = time.monotonic() + fixture.get("deadline_ms", 10_000) / 1000

        try:
            for solution in solve_function(
                algorithm_board,
                deadline=deadline,
                node_counter=nodes,
                backtrack_counter=backtracks,
            ):
                solution_count += 1

                if len(solutions) < 15:
                    serialized = serialize_grid(solution)
                    solutions.append(serialized)

                    assert not validate_board(solution)

                    for row in range(9):
                        for col in range(9):
                            if board[row][col] != ".":
                                assert solution[row][col] == board[row][col]

        except SearchTimeout:
            timed_out = True

        assert algorithm_board == original_board

        if timed_out and solution_count < 2:
            status = "timeout"
        elif solution_count == 0:
            status = "unsolvable"
        elif solution_count == 1:
            status = "unique"
        else:
            status = "multiple"

        acceptable_statuses = expected.get("acceptable_statuses")

        if acceptable_statuses is None:
            acceptable_statuses = [expected["expected_status"]]

        assert status in acceptable_statuses, (
            f"{fixture['id']} failed during cross-algorithm testing: "
            f"expected one of {acceptable_statuses}, got {status}"
        )

        if "acceptable_statuses" in expected:
            if status == "timeout":
                assert solution_count == 0
            elif status == "unique":
                assert solution_count == 1
                assert not timed_out

            continue

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

        results[algorithm_id] = {
            "status": status,
            "solution_count": solution_count,
            "solutions": solutions,
            "timed_out": timed_out,
        }

    # Compare completed searches with exact, manageable solution counts.
    completed_results = [result for result in results.values() if not result["timed_out"]]

    if (
        len(completed_results) == len(results)
        and fixture["count_type"] == "exact"
        and fixture["expected_solution_count"] <= 15
    ):
        reference = completed_results[0]

        for result in completed_results[1:]:
            assert result["status"] == reference["status"]
            assert result["solution_count"] == reference["solution_count"]

            assert set(result["solutions"]) == set(reference["solutions"]), (
                f"Solution sets differ for fixture {fixture['id']}"
            )
