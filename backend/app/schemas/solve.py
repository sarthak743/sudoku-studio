
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import SolverStatus


Algorithm = Literal["A1", "A2", "A3", "A4", "all"]


class SolveRequest(BaseModel):
    grid: str
    algorithm: Algorithm = "all"
    limit: int = Field(default=10, ge=1, le=15)
    offset: int = Field(default=0, ge=0)


class SolveResponse(BaseModel):
    status: SolverStatus
    solution_count: int = Field(ge=0)
    solutions: list[str] = Field(max_length=15)
    count_capped: bool = False
    timed_out: bool = False
    time_ms: float = Field(ge=0)
    nodes_visited: int = Field(ge=0)
    backtracks: int = Field(ge=0)
    algorithm: str


class AlgorithmRunResult(BaseModel):
    algorithm: str
    status: SolverStatus
    solution_count: int = Field(ge=0)
    time_ms: float = Field(ge=0)
    nodes_visited: int = Field(ge=0)
    backtracks: int = Field(ge=0)
    timed_out: bool = False


class SolveAllResponse(BaseModel):
    selected_result: SolveResponse
    algorithm_results: list[AlgorithmRunResult]
