def validate_format(grid: str) -> None:
    if not isinstance(grid, str):
        raise ValueError("Grid must be a string.")

    if len(grid) != 81:
        raise ValueError("Grid must contain exactly 81 characters.")

    allowed_chars = set("0123456789.")

    if not all(char in allowed_chars for char in grid):
        raise ValueError("Grid contains unsupported characters.")


def parse_grid(grid: str) -> list[list[str]]:
    validate_format(grid)

    normalized_grid = grid.replace("0", ".")

    board = [list(normalized_grid[i : i + 9]) for i in range(0, 81, 9)]

    return board


def serialize_grid(board: list[list[str]]) -> str:
    if len(board) != 9 or any(len(row) != 9 for row in board):
        raise ValueError("Board must be a 9x9 grid.")

    return "".join("".join(row) for row in board)
