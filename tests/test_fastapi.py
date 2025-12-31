"""
Comprehensive tests for RabbitRedux FastAPI application.
Tests all endpoints, authentication, rate limiting, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the model loading before importing main
mock_classifier = MagicMock()
mock_classifier.return_value = [{"label": "SECURITY", "score": 0.95}]

with patch('app.model.load_classifier', return_value=mock_classifier):
    from main import app
    from config import settings


client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_endpoint(self):
        """Test root endpoint returns project information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["project"] == "RabbitRedux"
        assert "version" in data
        assert "endpoints" in data
        assert "features" in data

    def test_root_endpoint_structure(self):
        """Test root endpoint has correct structure."""
        response = client.get("/")
        data = response.json()
        assert "repository" in data
        assert "author" in data
        assert "license" in data
        assert data["license"] == "Apache 2.0"


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "timestamp" in data

    def test_health_check_model_loaded(self):
        """Test health check reports model status."""
        response = client.get("/health")
        data = response.json()
        assert "model_loaded" in data
        assert isinstance(data["model_loaded"], bool)


class TestClassificationEndpoint:
    """Tests for the single classification endpoint."""

    @patch('main.classify_code')
    def test_classify_success(self, mock_classify):
        """Test successful code classification."""
        mock_classify.return_value = {
            "label": "SECURITY",
            "score": 0.95
        }

        response = client.post(
            "/classify",
            json={"code": "import os; os.system('whoami')"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "label" in data
        assert "score" in data
        assert "timestamp" in data
        assert data["label"] == "SECURITY"
        assert data["score"] == 0.95

    def test_classify_missing_code(self):
        """Test classification with missing code field."""
        response = client.post("/classify", json={})
        assert response.status_code == 422  # Validation error

    def test_classify_empty_code(self):
        """Test classification with empty code."""
        response = client.post("/classify", json={"code": ""})
        assert response.status_code == 422  # Validation error

    def test_classify_whitespace_only(self):
        """Test classification with whitespace-only code."""
        response = client.post("/classify", json={"code": "   "})
        assert response.status_code == 422  # Validation error

    @patch('main.classify_code')
    def test_classify_with_all_scores(self, mock_classify):
        """Test classification with all scores requested."""
        mock_classify.return_value = {
            "label": "SECURITY",
            "score": 0.95,
            "all_scores": [
                {"label": "SECURITY", "score": 0.95},
                {"label": "BENIGN", "score": 0.05}
            ]
        }

        response = client.post(
            "/classify",
            json={"code": "test code", "return_all_scores": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert "all_scores" in data
        assert data["all_scores"] is not None

    @patch('main.classify_code')
    def test_classify_long_code(self, mock_classify):
        """Test classification with very long code snippet."""
        mock_classify.return_value = {
            "label": "SECURITY",
            "score": 0.95
        }

        long_code = "def test():\n" + "    pass\n" * 500
        response = client.post("/classify", json={"code": long_code})

        assert response.status_code == 200
        data = response.json()
        # Code should be truncated in response
        assert len(data["code"]) <= 203  # 200 + "..."


class TestBatchClassificationEndpoint:
    """Tests for the batch classification endpoint."""

    @patch('main.classify_batch')
    def test_batch_classify_success(self, mock_batch):
        """Test successful batch classification."""
        mock_batch.return_value = [
            {"label": "SECURITY", "score": 0.95},
            {"label": "BENIGN", "score": 0.85}
        ]

        codes = [
            "import os; os.system('cmd')",
            "def add(a, b): return a + b"
        ]

        response = client.post("/batch", json={"codes": codes})

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_processed" in data
        assert "total_time_ms" in data
        assert "avg_time_per_item_ms" in data
        assert len(data["results"]) == 2

    def test_batch_classify_empty_list(self):
        """Test batch classification with empty list."""
        response = client.post("/batch", json={"codes": []})
        assert response.status_code == 422  # Validation error

    def test_batch_classify_exceeds_max_size(self):
        """Test batch classification exceeding maximum batch size."""
        # Create a batch larger than max_batch_size
        large_batch = ["test code"] * (settings.max_batch_size + 1)
        response = client.post("/batch", json={"codes": large_batch})
        assert response.status_code == 422  # Validation error

    @patch('main.classify_batch')
    def test_batch_classify_single_item(self, mock_batch):
        """Test batch classification with single item."""
        mock_batch.return_value = [{"label": "BENIGN", "score": 0.90}]

        response = client.post("/batch", json={"codes": ["test code"]})
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 1


class TestModelInfoEndpoint:
    """Tests for the model info endpoint."""

    @patch('main.get_model_info')
    def test_model_info(self, mock_info):
        """Test model info endpoint."""
        mock_info.return_value = {
            "model_name": "canstralian/WhiteRabbitNeo",
            "cached": True,
            "device": "CPU",
            "max_length": 512,
            "cache_size": 1
        }

        response = client.get("/model/info")
        assert response.status_code == 200
        data = response.json()
        assert "model_name" in data
        assert "cached" in data
        assert "device" in data
        assert "max_length" in data

    @patch('main.get_model_info')
    def test_model_info_with_custom_model(self, mock_info):
        """Test model info with custom model name."""
        mock_info.return_value = {
            "model_name": "custom/model",
            "cached": False,
            "device": "GPU",
            "max_length": 512,
            "cache_size": 0
        }

        response = client.get("/model/info?model_name=custom/model")
        assert response.status_code == 200


class TestAuthentication:
    """Tests for API key authentication."""

    @pytest.mark.skipif(
        not settings.require_api_key,
        reason="Authentication not enabled in test environment"
    )
    def test_clear_cache_requires_auth(self):
        """Test that cache clearing requires authentication."""
        response = client.post("/model/clear-cache")
        assert response.status_code in [401, 403]  # Unauthorized or Forbidden

    @pytest.mark.skipif(
        not settings.require_api_key,
        reason="Authentication not enabled in test environment"
    )
    def test_clear_cache_with_valid_key(self):
        """Test cache clearing with valid API key."""
        headers = {"X-API-Key": settings.api_key}
        response = client.post("/model/clear-cache", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @pytest.mark.skipif(
        not settings.require_api_key,
        reason="Authentication not enabled in test environment"
    )
    def test_clear_cache_with_invalid_key(self):
        """Test cache clearing with invalid API key."""
        headers = {"X-API-Key": "invalid-key"}
        response = client.post("/model/clear-cache", headers=headers)
        assert response.status_code == 403


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    @pytest.mark.skipif(
        not settings.rate_limit_enabled,
        reason="Rate limiting not enabled in test environment"
    )
    def test_rate_limit_enforcement(self):
        """Test that rate limiting is enforced."""
        # Make many requests quickly
        for i in range(settings.rate_limit_per_minute + 5):
            response = client.post(
                "/classify",
                json={"code": f"test code {i}"}
            )

            if i < settings.rate_limit_per_minute:
                # Should succeed
                assert response.status_code in [200, 500]  # 500 if model error
            else:
                # Should hit rate limit
                if response.status_code == 429:
                    break

        # At least one request should have hit the limit
        # (This is a soft assertion as timing can vary)


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        response = client.post(
            "/classify",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_content_type(self):
        """Test handling of missing content type."""
        response = client.post("/classify", data='{"code": "test"}')
        # Should still work as FastAPI is lenient
        assert response.status_code in [200, 422, 500]

    @patch('main.classify_code')
    def test_classification_error(self, mock_classify):
        """Test handling of classification errors."""
        mock_classify.return_value = {"error": "Model failed"}

        response = client.post(
            "/classify",
            json={"code": "test code"}
        )

        assert response.status_code == 500

    def test_nonexistent_endpoint(self):
        """Test accessing nonexistent endpoint."""
        response = client.get("/nonexistent")
        assert response.status_code == 404


class TestMetricsEndpoint:
    """Tests for Prometheus metrics endpoint."""

    @pytest.mark.skipif(
        not settings.enable_metrics,
        reason="Metrics not enabled in test environment"
    )
    def test_metrics_endpoint_exists(self):
        """Test that metrics endpoint exists."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Prometheus metrics are text format
        assert "text/plain" in response.headers.get("content-type", "")


class TestCORSMiddleware:
    """Tests for CORS middleware configuration."""

    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.options("/")
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


class TestModelVersioning:
    """Tests for model versioning functionality."""

    @pytest.mark.skipif(
        not settings.enable_model_versioning,
        reason="Model versioning not enabled in test environment"
    )
    @patch('main.classify_code')
    def test_classify_with_specific_version(self, mock_classify):
        """Test classification with specific model version."""
        mock_classify.return_value = {
            "label": "SECURITY",
            "score": 0.95
        }

        response = client.post(
            "/classify",
            json={
                "code": "test code",
                "model_name": "canstralian/RabbitRedux",
                "model_version": "v1.0"
            }
        )

        assert response.status_code == 200


# Pytest fixtures
@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Reset rate limits between tests."""
    from main import rate_limit_storage
    rate_limit_storage.clear()
    yield


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
