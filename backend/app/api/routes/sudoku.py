
from fastapi import APIRouter

from app.schemas.solve import (
    SolveRequest,
    SolveResponse,
    SolveAllResponse,
)
from app.schemas.validation import (
    GridRequest,
    ValidationResponse,
)
from app.services.validation_service import validate_sudoku
from app.services.solver_service import (
    solve_with_algorithm,
    solve_with_all_algorithms,
)

router = APIRouter(prefix="/api", tags=["Sudoku"])


@router.post("/validate", response_model=ValidationResponse)
def validate_endpoint(request: GridRequest):
    return validate_sudoku(request.grid)



@router.post(
    "/solve",
    response_model=SolveResponse | SolveAllResponse,
)
def solve_endpoint(request: SolveRequest):
    if request.algorithm == "all":
        return solve_with_all_algorithms(request.grid)

    return solve_with_algorithm(
        request.grid,
        request.algorithm,
    )

