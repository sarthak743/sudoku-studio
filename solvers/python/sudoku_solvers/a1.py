import time
from collections.abc import Generator


class SearchTimeout(Exception):
    pass


def is_valid_placement(board: list[list[str]], row: int, col: int, digit: str) -> bool:
    if digit in board[row]:
        return False

    if any(board[r][col] == digit for r in range(9)):
        return False

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3

    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] == digit:
                return False

    return True


def solve_a1(
    board: list[list[str]],
    deadline: float | None = None,
    node_counter: list[int] | None = None,
    backtrack_counter: list[int] | None = None,
) -> Generator[list[list[str]]]:

    if node_counter is None:
        node_counter = [0]

    if backtrack_counter is None:
        backtrack_counter = [0]

    node_counter[0] += 1

    if node_counter[0] % 1024 == 0:
        if deadline is not None and time.monotonic() >= deadline:
            raise SearchTimeout

    for row in range(9):
        for col in range(9):
            if board[row][col] == ".":
                for digit in "123456789":
                    if is_valid_placement(board, row, col, digit):
                        board[row][col] = digit
                        found_solution = False
                        completed = False

                        try:
                            for solution in solve_a1(
                                board,
                                deadline,
                                node_counter,
                                backtrack_counter,
                            ):
                                found_solution = True
                                yield solution

                            completed = True

                        finally:
                            board[row][col] = "."

                        if completed and not found_solution:
                            backtrack_counter[0] += 1

                return

    yield [row[:] for row in board]
