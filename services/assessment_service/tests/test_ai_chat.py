import pytest
import requests

@pytest.fixture
def gateway_url():
    return "http://localhost:8080"

@pytest.fixture
def user_token(gateway_url):
    login_data = {"email": "test@example.com", "password": "li"}
    response = requests.post(f"{gateway_url}/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


def test_chat_with_ai(gateway_url, user_token):
    chat_message = {"message": "I enjoy programming and solving challenging problems."}
    headers = {"Authorization": f"Bearer {user_token}"}

    response = requests.post(f"{gateway_url}/ai_chat/chat/", json=chat_message, headers=headers)
    assert response.status_code == 200

    response_json = response.json()
    assert "response" in response_json

    if response_json.get("recommendation"):
        assert len(response_json["recommendation"]) == 3
        for career in response_json["recommendation"]:
            assert "title" in career
            assert "description" in career
            assert "match_percentage" in career


def test_display_recommendations(gateway_url, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = requests.get(f"{gateway_url}/ai_chat/career_recommendations/", headers=headers)

    if response.status_code == 200:
        recommendations = response.json()
        assert len(recommendations) == 3
        for career in recommendations:
            assert "id" in career
            assert "title" in career
            assert "description" in career

    elif response.status_code == 404:
        assert response.json()["detail"] == "No career recommendations found. Try answering more questions."


def test_select_career(gateway_url, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    career_data = {"career_id": 1} 

    response = requests.post(f"{gateway_url}/ai_chat/select_career/", json=career_data, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        assert "message" in response_json
        assert "career" in response_json
        assert response_json["career"]["id"] == career_data["career_id"]
    elif response.status_code == 404:
        assert response.json()["detail"] == "No career recommendations found. Try answering more questions."
