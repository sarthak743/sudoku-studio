
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    internal_exception_handler,
)


@pytest.fixture
def test_app():
    app = FastAPI()

    app.add_exception_handler(
        HTTPException,
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

    @app.get("/http-error")
    def http_error():
        raise HTTPException(status_code=404, detail="Resource not found.")

    @app.get("/validation-error")
    def validation_error(value: int):
        return {"value": value}

    @app.get("/internal-error")
    def internal_error():
        raise RuntimeError("Simulated internal failure.")

    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app, raise_server_exceptions=False)


def test_http_exception_handler(client):
    response = client.get("/http-error")

    assert response.status_code == 404
    assert response.json() == {
        "code": "HTTP_404",
        "message": "Resource not found.",
        "details": None,
    }


def test_validation_exception_handler(client):
    response = client.get("/validation-error?value=abc")

    assert response.status_code == 422

    data = response.json()

    assert data["code"] == "VALIDATION_ERROR"
    assert data["message"] == "Request validation failed."
    assert len(data["details"]["errors"]) > 0


def test_internal_exception_handler(client):
    response = client.get("/internal-error")

    assert response.status_code == 500
    assert response.json() == {
        "code": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected internal server error occurred.",
        "details": None,
    }
