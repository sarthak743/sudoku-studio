
from pydantic import BaseModel, Field, field_validator


class GridRequest(BaseModel):
    grid: str

    @field_validator("grid")
    @classmethod
    def validate_grid_format(cls, value: str) -> str:
        if len(value) != 81:
            raise ValueError("Grid must contain exactly 81 characters.")

        if any(char not in "0123456789." for char in value):
            raise ValueError(
                "Grid may contain only digits 0-9 and periods."
            )

        return value


class CellPosition(BaseModel):
    row: int = Field(ge=0, le=8)
    col: int = Field(ge=0, le=8)


class ValidationResponse(BaseModel):
    valid: bool
    conflicts: list[CellPosition] = Field(default_factory=list)
