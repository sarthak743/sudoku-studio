import time
from dataclasses import dataclass

from sudoku_solvers.a1 import SearchTimeout, solve_a1
from sudoku_solvers.parser import parse_grid, serialize_grid, validate_format
from sudoku_solvers.validator import classify_completed_grid, validate_board


@dataclass
class SolverResult:
    status: str
    solution_count: int
    solutions: list[str]
    timed_out: bool = False
    count_capped: bool = False
    time_ms: float = 0.0
    nodes_visited: int = 0
    backtracks: int = 0
    algorithm: str = "A1"


def solve_sudoku(
    grid: str,
    deadline_ms: int = 10_000,
    max_solutions: int = 15,
) -> SolverResult:
    try:
        validate_format(grid)
        board = parse_grid(grid)
    except ValueError:
        return SolverResult("invalid_format", 0, [])

    conflicts = validate_board(board)

    if conflicts:
        return SolverResult("invalid", 0, [])

    classification = classify_completed_grid(board)

    if classification == "already_solved":
        return SolverResult(
            "already_solved",
            1,
            [serialize_grid(board)],
        )

    solutions = []
    solution_count = 0
    timed_out = False

    node_counter = [0]
    backtrack_counter = [0]

    deadline = time.monotonic() + deadline_ms / 1000
    start_time = time.perf_counter()

    try:
        for solution in solve_a1(
            board,
            deadline=deadline,
            node_counter=node_counter,
            backtrack_counter=backtrack_counter,
        ):
            solution_count += 1

            if len(solutions) < max_solutions:
                solutions.append(serialize_grid(solution))

    except SearchTimeout:
        timed_out = True

    time_ms = (time.perf_counter() - start_time) * 1000

    if timed_out and solution_count < 2:
        status = "timeout"
    elif solution_count == 0:
        status = "unsolvable"
    elif solution_count == 1:
        status = "unique"
    else:
        status = "multiple"

    return SolverResult(
        status=status,
        solution_count=solution_count,
        solutions=solutions,
        timed_out=timed_out,
        count_capped=False,
        time_ms=round(time_ms, 3),
        nodes_visited=node_counter[0],
        backtracks=backtrack_counter[0],
        algorithm="A1",
    )
