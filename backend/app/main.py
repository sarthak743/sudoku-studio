
from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    internal_exception_handler,
)

from app.api.routes.health import router as health_router
from app.api.routes.sudoku import router as sudoku_router

app = FastAPI(
    title="Sudoku Studio API",
    description="Backend API for Sudoku Studio.",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(sudoku_router)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    internal_exception_handler,
)
