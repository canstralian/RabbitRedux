import pytest
import json
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def client():
    """Set up a test client for the Flask app."""
    app = create_app('testing')
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


def test_health_endpoint(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data
    assert data["status"] == "healthy"


@patch('app.routes.get_classifier')
def test_classify_endpoint_valid(mock_get_classifier, client):
    """Test the /classify endpoint with a valid code snippet."""
    # Mock the classifier
    mock_classifier = MagicMock()
    mock_classifier.return_value = [{"label": "Python Function", "score": 0.98}]
    mock_get_classifier.return_value = mock_classifier

    response = client.post(
        "/classify",
        data=json.dumps({"code": "def hello(): print('Hello, world!')"}),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "classification" in data
    assert len(data["classification"]) > 0


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


def test_classify_endpoint_code_too_long(client):
    """Test the /classify endpoint with code snippet that's too long."""
    response = client.post(
        "/classify",
        data=json.dumps({"code": "a" * 10001}),  # Exceeds 10000 char limit
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "too long" in data["error"].lower()
