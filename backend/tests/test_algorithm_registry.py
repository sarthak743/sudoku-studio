
import pytest

from app.services.algorithm_registry import (
    ALGORITHM_REGISTRY,
    get_algorithm,
    get_algorithm_ids,
)

from sudoku_solvers.a1 import solve_a1
from sudoku_solvers.a2 import solve_a2
from sudoku_solvers.a3 import solve_a3
from sudoku_solvers.a4 import solve_a4


def test_registry_contains_all_algorithms():
    assert get_algorithm_ids() == ["A1", "A2", "A3", "A4"]


@pytest.mark.parametrize(
    "algorithm_id, expected_function",
    [
        ("A1", solve_a1),
        ("A2", solve_a2),
        ("A3", solve_a3),
        ("A4", solve_a4),
    ],
)
def test_registry_returns_correct_function(
    algorithm_id,
    expected_function,
):
    assert get_algorithm(algorithm_id) is expected_function


def test_unsupported_algorithm():
    with pytest.raises(ValueError):
        get_algorithm("A5")


def test_registry_has_exactly_four_algorithms():
    assert len(ALGORITHM_REGISTRY) == 4
