from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.errors import ErrorResponse


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    error = ErrorResponse(
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        details=None,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    error = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Request validation failed.",
        details={"errors": exc.errors()},
    )

    return JSONResponse(
        status_code=422,
        content=error.model_dump(),
    )


async def internal_exception_handler(
    request: Request,
    exc: Exception,
):
    error = ErrorResponse(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected internal server error occurred.",
        details=None,
    )

    return JSONResponse(
        status_code=500,
        content=error.model_dump(),
    )