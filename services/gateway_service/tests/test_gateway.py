import pytest
import requests

@pytest.fixture
def gateway_url():
    return "http://localhost:8080"


def test_gateway_health(gateway_url):
    response = requests.get(f"{gateway_url}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_gateway_users_register(gateway_url):
    user_data = {
        "username": "tesstusers",
        "email": "stestsuser@example.com",
        "password": "testpassword"
    }

    response = requests.post(f"{gateway_url}/users/register", json=user_data)
    assert response.status_code == 201

    response_json = response.json()
    assert "id" in response_json
    assert response_json["username"] == user_data["username"]
    assert response_json["email"] == user_data["email"]


def test_gateway_auth_login(gateway_url):
    login_data = {
        "username": "testusers",
        "email": "stestuser@example.com",
        "password": "testpassword"
    }

    response = requests.post(f"{gateway_url}/auth/login", json=login_data)
    assert response.status_code == 200

    response_json = response.json()
    assert "access_token" in response_json
    assert response_json["token_type"] == "bearer"
