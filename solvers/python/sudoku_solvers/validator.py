def find_row_conflicts(board: list[list[str]]) -> list[tuple[int, int]]:
    conflicts = []

    for row_index, row in enumerate(board):
        seen = {}

        for col_index, digit in enumerate(row):
            if digit == ".":
                continue

            if digit in seen:
                conflicts.append((row_index, col_index))
                conflicts.append((row_index, seen[digit]))
            else:
                seen[digit] = col_index

    return sorted(set(conflicts))


def find_column_conflicts(board: list[list[str]]) -> list[tuple[int, int]]:
    conflicts = []

    for col_index in range(9):
        seen = {}

        for row_index in range(9):
            digit = board[row_index][col_index]

            if digit == ".":
                continue

            if digit in seen:
                conflicts.append((row_index, col_index))
                conflicts.append((seen[digit], col_index))
            else:
                seen[digit] = row_index

    return sorted(set(conflicts))


def find_box_conflicts(board: list[list[str]]) -> list[tuple[int, int]]:
    conflicts = []

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            seen = {}

            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    digit = board[row][col]

                    if digit == ".":
                        continue

                    if digit in seen:
                        conflicts.append((row, col))
                        conflicts.append(seen[digit])
                    else:
                        seen[digit] = (row, col)

    return sorted(set(conflicts))


def validate_board(board: list[list[str]]) -> list[tuple[int, int]]:
    conflicts = set()

    conflicts.update(find_row_conflicts(board))
    conflicts.update(find_column_conflicts(board))
    conflicts.update(find_box_conflicts(board))

    return sorted(conflicts)


def validate_input(grid: str) -> list[tuple[int, int]]:
    from sudoku_solvers.parser import parse_grid

    board = parse_grid(grid)
    return validate_board(board)


def classify_completed_grid(board: list[list[str]]) -> str:
    if validate_board(board):
        return "invalid"

    if all("." not in row for row in board):
        return "already_solved"

    return "incomplete"
