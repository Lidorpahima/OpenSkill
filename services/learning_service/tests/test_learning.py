import pytest
import requests
from unittest import mock
import json

@pytest.fixture
def gateway_url():
    return "http://localhost:8080"

@pytest.fixture
def user_token(gateway_url):
    login_data = {"email": "test@example.com", "password": "li"}
    response = requests.post(f"{gateway_url}/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

def test_create_goal(gateway_url, user_token):
    goal_data = {
        "title": "Learn Python",
        "description": "Master Python programming language"
    }
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.post(f"{gateway_url}/learning/create_goal/", json=goal_data, headers=headers)
    
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["title"] == goal_data["title"]
    assert response_json["description"] == goal_data["description"]
    assert "id" in response_json
    assert "progress" in response_json
    assert response_json["progress"] == 0.0
    
    return response_json["id"]

def test_get_goals(gateway_url, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{gateway_url}/learning/goals/", headers=headers)
    
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    
    if response_json:
        goal = response_json[0]
        assert "id" in goal
        assert "title" in goal
        assert "description" in goal
        assert "progress" in goal
        assert "user_id" in goal

def test_update_goal(gateway_url, user_token):
    goal_id = test_create_goal(gateway_url, user_token)
    
    updated_goal_data = {
        "title": "Learn Python Advanced",
        "description": "Master advanced Python concepts"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.put(
        f"{gateway_url}/learning/update_goal/{goal_id}", 
        json=updated_goal_data, 
        headers=headers
    )
    
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["title"] == updated_goal_data["title"]
    assert response_json["description"] == updated_goal_data["description"]
    assert response_json["id"] == goal_id

def test_search_goals(gateway_url, user_token):
    goal_data = {
        "title": "UniqueSearchTitle",
        "description": "UniqueSearchDescription"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    create_response = requests.post(f"{gateway_url}/learning/create_goal/", json=goal_data, headers=headers)
    assert create_response.status_code == 200
    
    search_title_response = requests.get(
        f"{gateway_url}/learning/search?title=UniqueSearch", 
        headers=headers
    )
    assert search_title_response.status_code == 200
    title_results = search_title_response.json()
    assert len(title_results) > 0
    assert any(goal["title"] == "UniqueSearchTitle" for goal in title_results)
    
    search_desc_response = requests.get(
        f"{gateway_url}/learning/search?description=UniqueSearchDesc", 
        headers=headers
    )
    assert search_desc_response.status_code == 200
    desc_results = search_desc_response.json()
    assert len(desc_results) > 0
    assert any(goal["description"] == "UniqueSearchDescription" for goal in desc_results)

def test_delete_goal(gateway_url, user_token):
    goal_id = test_create_goal(gateway_url, user_token)
    
    headers = {"Authorization": f"Bearer {user_token}"}
    delete_response = requests.delete(f"{gateway_url}/learning/delete_goal/{goal_id}", headers=headers)
    
    assert delete_response.status_code == 200
    delete_json = delete_response.json()
    assert delete_json["id"] == goal_id
    
    get_response = requests.get(f"{gateway_url}/learning/goals/", headers=headers)
    assert get_response.status_code == 200
    goals = get_response.json()
    assert not any(goal["id"] == goal_id for goal in goals)

def test_invalid_token():
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5OTk5IiwiZXhwIjoxNjk5OTk5OTk5fQ.invalid_signature"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    
    response = requests.get("http://localhost:8080/learning/goals/", headers=headers)
    
    assert response.status_code == 401

def test_missing_token():
    response = requests.get("http://localhost:8080/learning/goals/")
    assert response.status_code == 401