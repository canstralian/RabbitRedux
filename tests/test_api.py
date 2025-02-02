import pytest
import json
from app import create_app

@pytest.fixture
def client():
    """Set up a test client for the Flask app."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_endpoint(client):
    """Test the root (/) endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "project" in data
    assert data["project"] == "RabbitRedux - WhiteRabbitNeo Code Classification Model"

def test_classify_endpoint_valid(client):
    """Test the /classify endpoint with a valid code snippet."""
    response = client.post(
        "/classify",
        data=json.dumps({"code": "def hello(): print('Hello, world!')"}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "classification" in data

def test_classify_endpoint_missing_code(client):
    """Test the /classify endpoint with missing 'code' field."""
    response = client.post(
        "/classify",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Missing 'code' field in request"

def test_classify_endpoint_invalid_json(client):
    """Test the /classify endpoint with invalid JSON format."""
    response = client.post(
        "/classify",
        data="invalid_json",
        content_type="application/json"
    )
    assert response.status_code == 400  # Flask should handle invalid JSON gracefully