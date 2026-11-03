from sudoku_solvers.solver import solve_sudoku


def test_solver_finds_unique_solution():
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

    result = solve_sudoku(grid)

    assert result.status == "unique"
    assert result.solution_count == 1


def test_solver_detects_invalid_format():
    result = solve_sudoku("12345")

    assert result.status == "invalid_format"


def test_solver_detects_invalid_grid():
    grid = "550070000600195000098000060800060003400803001700020006060000280000419005000080079"

    result = solve_sudoku(grid)

    assert result.status == "invalid"


def test_solver_detects_already_solved():
    grid = "534678912672195348198342567859761423426853791713924856961537284287419635345286179"

    result = solve_sudoku(grid)

    assert result.status == "already_solved"
    assert result.solution_count == 1


def test_solver_detects_unsolvable():
    grid = "123456780000000009000000000000000000000000000000000000000000000000000000000000000"

    result = solve_sudoku(grid)

    assert result.status == "unsolvable"
    assert result.solution_count == 0


def test_solver_stores_at_most_15_solutions():
    result = solve_sudoku("." * 81, deadline_ms=1000)

    assert len(result.solutions) <= 15
    assert result.count_capped is False


def test_solver_respects_deadline():
    result = solve_sudoku("." * 81, deadline_ms=1)

    assert result.timed_out is True


def test_solver_finds_multiple_solutions():
    result = solve_sudoku("." * 81, deadline_ms=1000)

    assert result.status == "multiple"
    assert result.solution_count >= 2


def test_solver_returns_metadata():
    grid = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

    result = solve_sudoku(grid)

    assert result.algorithm == "A1"
    assert result.time_ms >= 0
    assert result.nodes_visited > 0
    assert result.backtracks >= 0
    assert result.count_capped is False


def test_solver_respects_solution_storage_limit():
    result = solve_sudoku("." * 81, deadline_ms=1000, max_solutions=2)

    assert len(result.solutions) <= 2
