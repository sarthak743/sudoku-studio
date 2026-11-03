
import time
from concurrent.futures import ThreadPoolExecutor

from sudoku_solvers.a1 import SearchTimeout
from sudoku_solvers.parser import parse_grid, serialize_grid, validate_format
from sudoku_solvers.validator import (
    classify_completed_grid,
    validate_board,
)

from app.core.config import settings
from app.schemas.common import SolverStatus
from app.schemas.solve import (
    AlgorithmRunResult,
    SolveAllResponse,
    SolveResponse,
)
from app.services.algorithm_registry import (
    get_algorithm,
    get_algorithm_ids,
)


def _solve_one(
    grid: str,
    algorithm_id: str,
    deadline_ms: int,
    max_solutions: int,
) -> SolveResponse:
    try:
        board = parse_grid(grid)
    except ValueError:
        return SolveResponse(
            status=SolverStatus.INVALID_FORMAT,
            solution_count=0,
            solutions=[],
            count_capped=False,
            timed_out=False,
            time_ms=0.0,
            nodes_visited=0,
            backtracks=0,
            algorithm=algorithm_id,
        )

    conflicts = validate_board(board)

    if conflicts:
        return SolveResponse(
            status=SolverStatus.INVALID,
            solution_count=0,
            solutions=[],
            time_ms=0,
            nodes_visited=0,
            backtracks=0,
            algorithm=algorithm_id,
        )

    if classify_completed_grid(board) == "already_solved":
        return SolveResponse(
            status=SolverStatus.ALREADY_SOLVED,
            solution_count=1,
            solutions=[serialize_grid(board)],
            time_ms=0,
            nodes_visited=0,
            backtracks=0,
            algorithm=algorithm_id,
        )

    solver = get_algorithm(algorithm_id)

    node_counter = [0]
    backtrack_counter = [0]
    solutions = []
    solution_count = 0
    timed_out = False

    start = time.perf_counter()
    deadline = time.monotonic() + deadline_ms / 1000

    try:
        for solution in solver(
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

    elapsed_ms = (time.perf_counter() - start) * 1000

    if timed_out and solution_count < 2:
        status = SolverStatus.TIMEOUT
    elif solution_count == 0:
        status = SolverStatus.UNSOLVABLE
    elif solution_count == 1:
        status = SolverStatus.UNIQUE
    else:
        status = SolverStatus.MULTIPLE

    return SolveResponse(
        status=status,
        solution_count=solution_count,
        solutions=solutions,
        count_capped=False,
        timed_out=timed_out,
        time_ms=round(elapsed_ms, 3),
        nodes_visited=node_counter[0],
        backtracks=backtrack_counter[0],
        algorithm=algorithm_id,
    )


def solve_with_algorithm(
    grid: str,
    algorithm_id: str,
) -> SolveResponse:
    return _solve_one(
        grid,
        algorithm_id,
        settings.solver_deadline_ms,
        settings.max_stored_solutions,
    )


def solve_with_all_algorithms(grid: str) -> SolveAllResponse:
    algorithm_ids = get_algorithm_ids()
    try:
        validate_format(grid)
    except ValueError:
        return SolveResponse(
            status=SolverStatus.INVALID_FORMAT,
            solution_count=0,
            solutions=[],
            count_capped=False,
            timed_out=False,
            time_ms=0.0,
            nodes_visited=0,
            backtracks=0,
            algorithm="all",
        )

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            algorithm_id: executor.submit(
                _solve_one,
                grid,
                algorithm_id,
                settings.solver_deadline_ms,
                settings.max_stored_solutions,
            )
            for algorithm_id in algorithm_ids
        }

        results = [
            futures[algorithm_id].result()
            for algorithm_id in algorithm_ids
        ]

    successful = [
        result
        for result in results
        if result.solution_count > 0
    ]

    selected = (
        min(successful, key=lambda result: result.time_ms)
        if successful
        else min(results, key=lambda result: result.time_ms)
    )

    timings = [
        AlgorithmRunResult(
            algorithm=result.algorithm,
            status=result.status,
            solution_count=result.solution_count,
            time_ms=result.time_ms,
            nodes_visited=result.nodes_visited,
            backtracks=result.backtracks,
            timed_out=result.timed_out,
        )
        for result in results
    ]

    return SolveAllResponse(
        selected_result=selected,
        algorithm_results=timings,
    )
