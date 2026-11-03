
from enum import Enum


class SolverStatus(str, Enum):
    INVALID_FORMAT = "invalid_format"
    INVALID = "invalid"
    ALREADY_SOLVED = "already_solved"
    UNSOLVABLE = "unsolvable"
    UNIQUE = "unique"
    MULTIPLE = "multiple"
    TIMEOUT = "timeout"
