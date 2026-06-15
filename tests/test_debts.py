import uuid

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def create_test_user():
    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{uuid.uuid4().hex[:8]}@gmail.com"
    password = "123456"

    client.post(
        "/auth/signup",
        json={
            "username": username,
            "email": email,
            "password": password,
            "is_staff": False,
            "is_active": True
        }
    )

    return username, password


def get_token():
    username, password = create_test_user()

    response = client.post(
        "/auth/login",
        json={
            "username_or_email": username,
            "password": password
        }
    )

    return response.json()["token"]["access_token"]


def test_create_debt():
    token = get_token()

    response = client.post(
        "/debt/create",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "debt_type": "owed_to",
            "person_name": "Ali",
            "amount": 100,
            "currency": "USD",
            "description": "Test debt",
            "date_due": "2026-12-31T12:00:00"
        }
    )

    assert response.status_code == 201


def test_get_debts():
    token = get_token()

    response = client.get(
        "/debt/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_get_owed_to_debts():
    token = get_token()

    response = client.get(
        "/debt/?debt_type=owed_to",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_get_individual_debts():
    token = get_token()

    response = client.get(
        "/debt/?debt_type=individual&person_name=Ali",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_update_debt():
    token = get_token()

    create_response = client.post(
        "/debt/create",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "debt_type": "owed_to",
            "person_name": "Ali",
            "amount": 100,
            "currency": "USD",
            "description": "Test",
            "date_due": "2026-12-31T12:00:00"
        }
    )

    debt_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/debt/update/{debt_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "debt_type": "owed_by",
            "person_name": "Ali",
            "amount": 200,
            "currency": "USD",
            "description": "Updated debt",
            "date_due": "2026-12-31T12:00:00"
        }
    )

    assert response.status_code == 200


def test_delete_debt():
    token = get_token()

    create_response = client.post(
        "/debt/create",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "debt_type": "owed_to",
            "person_name": "Ali",
            "amount": 100,
            "currency": "USD",
            "description": "Delete debt",
            "date_due": "2026-12-31T12:00:00"
        }
    )

    debt_id = create_response.json()["data"]["id"]

    response = client.delete(
        f"/debt/delete/{debt_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


