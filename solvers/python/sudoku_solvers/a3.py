import time
from collections.abc import Generator

from sudoku_solvers.a1 import SearchTimeout


def solve_a3(
    board: list[list[str]],
    deadline: float | None = None,
    node_counter: list[int] | None = None,
    backtrack_counter: list[int] | None = None,
) -> Generator[list[list[str]]]:

    if node_counter is None:
        node_counter = [0]

    if backtrack_counter is None:
        backtrack_counter = [0]

    def get_candidates(row: int, col: int) -> list[str]:
        used = set(board[row])

        used.update(board[r][col] for r in range(9))

        box_row = (row // 3) * 3
        box_col = (col // 3) * 3

        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                used.add(board[r][c])

        return [digit for digit in "123456789" if digit not in used]

    def search() -> Generator[list[list[str]]]:
        node_counter[0] += 1

        if node_counter[0] % 1024 == 0:
            if deadline is not None and time.monotonic() >= deadline:
                raise SearchTimeout

        best_cell = None
        best_candidates = None

        # Find the empty cell with the fewest candidates.
        # Row-major traversal provides deterministic tie-breaking.
        for row in range(9):
            for col in range(9):
                if board[row][col] == ".":
                    candidates = get_candidates(row, col)

                    if not candidates:
                        return

                    if best_candidates is None or len(candidates) < len(best_candidates):
                        best_cell = (row, col)
                        best_candidates = candidates

                    if len(best_candidates) == 1:
                        break

            if best_candidates is not None and len(best_candidates) == 1:
                break

        # No empty cells remain: puzzle solved.
        if best_cell is None:
            yield [row[:] for row in board]
            return

        row, col = best_cell

        found_solution = False

        for digit in best_candidates:
            board[row][col] = digit

            branch_found_solution = False
            branch_completed = False

            try:
                for solution in search():
                    branch_found_solution = True
                    found_solution = True
                    yield solution

                branch_completed = True

            finally:
                board[row][col] = "."

            if branch_completed and not branch_found_solution:
                backtrack_counter[0] += 1

        if not found_solution:
            backtrack_counter[0] += 1

    yield from search()
