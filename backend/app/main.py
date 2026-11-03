
from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.sudoku import router as sudoku_router

app = FastAPI(
    title="Sudoku Studio API",
    description="Backend API for Sudoku Studio.",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(sudoku_router)
