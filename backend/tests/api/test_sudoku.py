
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_GRID = (
    "530070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079"
)


def test_validate_endpoint():
    response = client.post(
        "/api/validate",
        json={"grid": VALID_GRID},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["conflicts"] == []


def test_solve_with_all_algorithms():
    response = client.post(
        "/api/solve",
        json={"grid": VALID_GRID},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["selected_result"]["status"] == "unique"
    assert len(data["algorithm_results"]) == 4


def test_solve_with_individual_algorithm():
    response = client.post(
        "/api/solve",
        json={
            "grid": VALID_GRID,
            "algorithm": "A3",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "unique"
    assert data["algorithm"] == "A3"


def test_invalid_algorithm_rejected():
    response = client.post(
        "/api/solve",
        json={
            "grid": VALID_GRID,
            "algorithm": "A5",
        },
    )

    assert response.status_code == 422



def test_invalid_grid_format_returns_invalid_format():
    response = client.post(
        "/api/solve",
        json={"grid": "123"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "invalid_format"
    assert response.json()["solution_count"] == 0


def test_unsupported_character_returns_invalid_format():
    response = client.post(
        "/api/solve",
        json={"grid": "x" * 81},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "invalid_format"

