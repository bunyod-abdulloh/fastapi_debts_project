from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

import uuid


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

    assert response.status_code == 200

    return response.json()["token"]["access_token"]


def test_signup():
    import uuid

    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{uuid.uuid4().hex[:8]}@gmail.com"
    password = f"password_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/auth/signup",
        json={
            "username": username,
            "email": email,
            "password": password,
            "is_staff": False,
            "is_active": True
        }
    )

    assert response.status_code == 201


def test_login():
    username, password = create_test_user()

    response = client.post(
        "/auth/login",
        json={
            "username_or_email": username,
            "password": password
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "access_token" in data["token"]
    assert "refresh_token" in data["token"]


def test_auth_me():
    token = get_token()

    response = client.get(
        "/auth/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_refresh():
    username, password = create_test_user()

    login_response = client.post(
        "/auth/login",
        json={
            "username_or_email": username,
            "password": password
        }
    )

    refresh_token = login_response.json()["token"]["refresh_token"]

    response = client.get(
        "/auth/login/refresh/",
        headers={
            "Authorization": f"Bearer {refresh_token}"
        }
    )

    assert response.status_code == 200
