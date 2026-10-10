import pytest

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


@pytest.mark.parametrize(
    "endpoint,fields",
    [
        (
            "/api/system/cpu",
            {"name", "usage", "physical_cores",
             "logical_cores", "frequency_mhz"}
        ),
        (
            "/api/system/memory",
            {"total", "used", "available", "percent"}
        ),
        (
            "/api/system/storage",
            {"volume", "total", "used", "free", "percent"}
        ),
        (
            "/api/system/info",
            {"os", "os_release", "architecture", "uptime"}
        )
    ]
)
def test_system_endpoint(endpoint, fields):
    response = client.get(endpoint)

    assert response.status_code == 200
    assert fields.issubset(response.json().keys())