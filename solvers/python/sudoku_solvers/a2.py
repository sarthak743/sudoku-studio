import time
from collections.abc import Generator

from sudoku_solvers.a1 import SearchTimeout

FULL_MASK = (1 << 9) - 1


def solve_a2(
    board: list[list[str]],
    deadline: float | None = None,
    node_counter: list[int] | None = None,
    backtrack_counter: list[int] | None = None,
) -> Generator[list[list[str]]]:

    if node_counter is None:
        node_counter = [0]

    if backtrack_counter is None:
        backtrack_counter = [0]

    row_masks = [0] * 9
    col_masks = [0] * 9
    box_masks = [0] * 9

    for row in range(9):
        for col in range(9):
            digit = board[row][col]

            if digit != ".":
                bit = 1 << (int(digit) - 1)
                box = (row // 3) * 3 + (col // 3)

                row_masks[row] |= bit
                col_masks[col] |= bit
                box_masks[box] |= bit

    def search() -> Generator[list[list[str]]]:
        node_counter[0] += 1

        if node_counter[0] % 1024 == 0:
            if deadline is not None and time.monotonic() >= deadline:
                raise SearchTimeout

        for row in range(9):
            for col in range(9):
                if board[row][col] == ".":
                    box = (row // 3) * 3 + (col // 3)

                    available = FULL_MASK & ~(row_masks[row] | col_masks[col] | box_masks[box])

                    while available:
                        bit = available & -available
                        available ^= bit

                        digit = str(bit.bit_length())

                        board[row][col] = digit
                        row_masks[row] |= bit
                        col_masks[col] |= bit
                        box_masks[box] |= bit

                        found_solution = False
                        completed = False

                        try:
                            for solution in search():
                                found_solution = True
                                yield solution

                            completed = True

                        finally:
                            board[row][col] = "."
                            row_masks[row] &= ~bit
                            col_masks[col] &= ~bit
                            box_masks[box] &= ~bit

                        if completed and not found_solution:
                            backtrack_counter[0] += 1

                    return

        yield [row[:] for row in board]

    yield from search()
