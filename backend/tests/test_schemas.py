
import pytest
from pydantic import ValidationError

from app.schemas.common import SolverStatus
from app.schemas.solve import SolveRequest, SolveResponse
from app.schemas.validation import (
    CellPosition,
    GridRequest,
    ValidationResponse,
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

VALID_SOLUTION = (
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


def test_solve_request_defaults():
    request = SolveRequest(grid=VALID_GRID)

    assert request.algorithm == "all"
    assert request.limit == 10
    assert request.offset == 0


def test_solve_request_custom_values():
    request = SolveRequest(
        grid=VALID_GRID,
        algorithm="A3",
        limit=5,
        offset=10,
    )

    assert request.algorithm == "A3"
    assert request.limit == 5
    assert request.offset == 10


@pytest.mark.parametrize(
    "grid",
    [
        "123",
        VALID_GRID[:-1],
        VALID_GRID + "1",
        "x" * 81,
    ],
)
def test_solve_request_accepts_malformed_grid_for_solver_classification(grid):
    request = SolveRequest(grid=grid)
    assert request.grid == grid

def test_invalid_algorithm():
    with pytest.raises(ValidationError):
        SolveRequest(grid=VALID_GRID, algorithm="A5")


@pytest.mark.parametrize("limit", [0, 16, -1])
def test_invalid_solution_limit(limit):
    with pytest.raises(ValidationError):
        SolveRequest(grid=VALID_GRID, limit=limit)


def test_negative_offset():
    with pytest.raises(ValidationError):
        SolveRequest(grid=VALID_GRID, offset=-1)


def test_grid_request_accepts_valid_grid():
    request = GridRequest(grid=VALID_GRID)

    assert request.grid == VALID_GRID


def test_cell_position():
    position = CellPosition(row=0, col=8)

    assert position.row == 0
    assert position.col == 8


def test_invalid_cell_position():
    with pytest.raises(ValidationError):
        CellPosition(row=9, col=0)


def test_validation_response():
    response = ValidationResponse(
        valid=False,
        conflicts=[
            CellPosition(row=0, col=2),
            CellPosition(row=1, col=2),
        ],
    )

    assert response.valid is False
    assert len(response.conflicts) == 2


def test_solve_response():
    response = SolveResponse(
        status=SolverStatus.UNIQUE,
        solution_count=1,
        solutions=[VALID_SOLUTION],
        count_capped=False,
        timed_out=False,
        time_ms=2.5,
        nodes_visited=10,
        backtracks=0,
        algorithm="A3",
    )

    assert response.status == SolverStatus.UNIQUE
    assert response.solution_count == 1
    assert len(response.solutions) == 1
