
from collections.abc import Callable, Generator

from sudoku_solvers.a1 import solve_a1
from sudoku_solvers.a2 import solve_a2
from sudoku_solvers.a3 import solve_a3
from sudoku_solvers.a4 import solve_a4

SolverFunction = Callable[..., Generator[list[list[str]], None, None]]

ALGORITHM_REGISTRY: dict[str, SolverFunction] = {
    "A1": solve_a1,
    "A2": solve_a2,
    "A3": solve_a3,
    "A4": solve_a4,
}


def get_algorithm(algorithm_id: str) -> SolverFunction:
    try:
        return ALGORITHM_REGISTRY[algorithm_id]
    except KeyError:
        raise ValueError(
            f"Unsupported algorithm: {algorithm_id}"
        ) from None


def get_algorithm_ids() -> list[str]:
    return list(ALGORITHM_REGISTRY.keys())
