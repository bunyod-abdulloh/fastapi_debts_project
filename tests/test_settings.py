import uuid
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_settings():
    token = get_token()

    response = client.get(
        "/settings/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "default_currency" in data["data"]
    assert "reminder_hours_before" in data["data"]


def test_update_settings():
    token = get_token()

    response = client.put(
        "/settings/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "default_currency": "USD",
            "reminder_hours_before": 12
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["default_currency"] == "USD"
    assert data["data"]["reminder_hours_before"] == 12
