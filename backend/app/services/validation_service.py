
from sudoku_solvers.parser import parse_grid, validate_format
from sudoku_solvers.validator import validate_board

from app.schemas.validation import (
    CellPosition,
    ValidationResponse,
)


def validate_sudoku(grid: str) -> ValidationResponse:
    try:
        validate_format(grid)
        board = parse_grid(grid)
    except ValueError:
        raise ValueError("Invalid Sudoku grid format.") from None

    conflicts = validate_board(board)

    return ValidationResponse(
        valid=len(conflicts) == 0,
        conflicts=[
            CellPosition(row=row, col=col)
            for row, col in conflicts
        ],
    )
