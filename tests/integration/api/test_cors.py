from fastapi.testclient import TestClient

from app.main import app


def test_cors_allows_configured_origins() -> None:
    with TestClient(app) as client:
        response = client.options(
            "api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )


def test_cors_rejects_unconfigured_origins() -> None:
    with TestClient(app) as client:
        response = client.options(
            "api/v1/health",
            headers={
                "Origin": "http://unknown-origin.co",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 400
        assert "access-control-allow-origin" not in response.headers
