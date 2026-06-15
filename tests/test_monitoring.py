import uuid
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_monitoring():
    token = get_token()

    response = client.get(
        "/monitoring/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "total_owed_to" in data["data"]
    assert "total_owed_by" in data["data"]
    assert "balance" in data["data"]


def test_monitoring_unauthorized():
    response = client.get("/monitoring/")

    assert response.status_code == 401
