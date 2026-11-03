import time
from collections.abc import Generator

from sudoku_solvers.a1 import SearchTimeout

FULL_MASK = (1 << 9) - 1


def solve_a4(
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

    def get_units():
        units = []

        for row in range(9):
            units.append([(row, col) for col in range(9)])

        for col in range(9):
            units.append([(row, col) for row in range(9)])

        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                units.append(
                    [
                        (row, col)
                        for row in range(box_row, box_row + 3)
                        for col in range(box_col, box_col + 3)
                    ]
                )

        return units

    units = get_units()

    def propagate() -> bool:
        while True:
            changed = False

            # Naked singles: row-major order.
            for row in range(9):
                for col in range(9):
                    if board[row][col] == ".":
                        candidates = get_candidates(row, col)

                        if not candidates:
                            return False

                        if len(candidates) == 1:
                            board[row][col] = candidates[0]
                            changed = True
                            break

                if changed:
                    break

            if changed:
                continue

            # Hidden singles: rows, columns, then boxes.
            for unit in units:
                for digit in "123456789":
                    empty_cells = [(row, col) for row, col in unit if board[row][col] == "."]

                    possible_cells = [
                        (row, col) for row, col in empty_cells if digit in get_candidates(row, col)
                    ]

                    if not possible_cells:
                        if any(board[row][col] == "." for row, col in unit):
                            # A missing digit with no available position
                            # makes this branch impossible.
                            digit_present = any(board[row][col] == digit for row, col in unit)
                            if not digit_present:
                                return False

                    if len(possible_cells) == 1:
                        row, col = possible_cells[0]
                        board[row][col] = digit
                        changed = True
                        break

                if changed:
                    break

            if changed:
                continue

            return True

    def search() -> Generator[list[list[str]]]:
        node_counter[0] += 1

        if node_counter[0] % 1024 == 0:
            if deadline is not None and time.monotonic() >= deadline:
                raise SearchTimeout

        original = [row[:] for row in board]

        try:
            if not propagate():
                return

            best_cell = None
            best_candidates = None

            # MRV with row-major tie-breaking.
            for row in range(9):
                for col in range(9):
                    if board[row][col] == ".":
                        candidates = get_candidates(row, col)

                        if not candidates:
                            return

                        if best_candidates is None or len(candidates) < len(best_candidates):
                            best_cell = (row, col)
                            best_candidates = candidates

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

        finally:
            for row in range(9):
                board[row][:] = original[row]

    yield from search()
