import json
from pathlib import Path

import pytest
from sudoku_solvers.solver import solve_sudoku

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "data" / "puzzles" / "edge_cases.json"

with FIXTURE_PATH.open(encoding="utf-8") as file:
    FIXTURES = json.load(file)


A1_FIXTURES = [
    fixture for fixture in FIXTURES if "algorithms" not in fixture or "A1" in fixture["algorithms"]
]


@pytest.mark.parametrize(
    "fixture",
    A1_FIXTURES,
    ids=lambda fixture: fixture["id"],
)
def test_a1_against_edge_cases(fixture):
    result = solve_sudoku(
        fixture["grid"],
        deadline_ms=fixture.get("deadline_ms", 10_000),
    )

    assert result.status == fixture["expected_status"]

    count_type = fixture["count_type"]
    expected_count = fixture["expected_solution_count"]

    if count_type == "exact":
        assert result.solution_count == expected_count

    elif count_type == "lower_bound":
        assert result.solution_count >= expected_count

    elif count_type == "not_applicable":
        assert result.solution_count == 0


def test_a1_stores_at_most_15_solutions():
    fixture = next(f for f in FIXTURES if f["id"] == "EC017")

    result = solve_sudoku(fixture["grid"])

    assert result.solution_count == 16
    assert len(result.solutions) == 15
    assert result.count_capped is False


def test_a1_solutions_are_deterministic():
    fixture = next(f for f in FIXTURES if f["id"] == "EC001")

    first = solve_sudoku(fixture["grid"])
    second = solve_sudoku(fixture["grid"])

    assert first.solutions == second.solutions
    assert first.solution_count == second.solution_count
