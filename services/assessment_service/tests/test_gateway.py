import pytest
import requests

@pytest.fixture
def gateway_url():
    return "http://localhost:8002"  
def test_gateway_health(gateway_url):
    response = requests.get(f"{gateway_url}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
