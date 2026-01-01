# RabbitRedux API Documentation

## Overview

RabbitRedux provides both **FastAPI** (recommended) and **Flask** (legacy) REST APIs for code classification using transformer-based machine learning models.

**Base URL (FastAPI):** `http://localhost:8000`
**Base URL (Flask):** `http://localhost:5000`

---

## Quick Start

### FastAPI (Production)

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload (development)
uvicorn main:app --reload

# Run with workers (production)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Flask (Legacy)

```bash
# Run Flask app
python app.py

# Or with Gunicorn
gunicorn wsgi:app --bind 0.0.0.0:5000
```

### Docker

```bash
# Build image
docker build -t rabbitredux .

# Run FastAPI (default)
docker run -p 8000:8000 rabbitredux

# Run Flask
docker run -p 5000:5000 rabbitredux gunicorn --bind 0.0.0.0:5000 wsgi:app
```

---

## FastAPI Endpoints

### 1. Root Endpoint

**GET /** - Get API information

**Response:**
```json
{
  "project": "RabbitRedux",
  "description": "WhiteRabbitNeo Code Classification Model",
  "version": "1.0.0",
  "environment": "development",
  "repository": "https://github.com/canstralian/RabbitRedux",
  "author": "Stephen de Jager (canstralian)",
  "license": "Apache 2.0",
  "endpoints": {
    "health": "/health",
    "classify": "/classify",
    "batch_classify": "/batch",
    "model_info": "/model/info",
    "metrics": "/metrics",
    "docs": "/docs"
  },
  "features": {
    "authentication": false,
    "batch_processing": true,
    "model_versioning": true,
    "rate_limiting": true,
    "metrics": true
  }
}
```

---

### 2. Health Check

**GET /health** - Check API health status

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "environment": "production",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Status Codes:**
- `200` - Service healthy
- `500` - Service unhealthy

---

### 3. Code Classification

**POST /classify** - Classify a single code snippet

**Request:**
```json
{
  "code": "import os; os.system('whoami')",
  "model_name": "canstralian/WhiteRabbitNeo",  // optional
  "model_version": "v1.0",  // optional
  "return_all_scores": false  // optional
}
```

**Response:**
```json
{
  "code": "import os; os.system('whoami')",
  "label": "SECURITY",
  "score": 0.95,
  "all_scores": null,
  "model_name": "canstralian/WhiteRabbitNeo",
  "timestamp": "2024-01-01T12:00:00",
  "processing_time_ms": 123.45
}
```

**With All Scores:**
```json
{
  "code": "...",
  "label": "SECURITY",
  "score": 0.95,
  "all_scores": [
    {"label": "SECURITY", "score": 0.95},
    {"label": "BENIGN", "score": 0.03},
    {"label": "SUSPICIOUS", "score": 0.02}
  ],
  "model_name": "canstralian/WhiteRabbitNeo",
  "timestamp": "2024-01-01T12:00:00",
  "processing_time_ms": 156.78
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid request (missing or empty code)
- `429` - Rate limit exceeded
- `500` - Classification error

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"code": "import subprocess; subprocess.call([\"ls\"])"}'
```

---

### 4. Batch Classification

**POST /batch** - Classify multiple code snippets (better performance)

**Request:**
```json
{
  "codes": [
    "def add(a, b): return a + b",
    "import os; os.system('rm -rf /')",
    "print('Hello World')"
  ],
  "model_name": "canstralian/WhiteRabbitNeo",  // optional
  "model_version": null,  // optional
  "return_all_scores": false  // optional
}
```

**Response:**
```json
{
  "results": [
    {
      "code": "def add(a, b): return a + b",
      "label": "BENIGN",
      "score": 0.98,
      "all_scores": null,
      "model_name": "canstralian/WhiteRabbitNeo",
      "timestamp": "2024-01-01T12:00:00",
      "processing_time_ms": null
    },
    {
      "code": "import os; os.system('rm -rf /')",
      "label": "SECURITY",
      "score": 0.99,
      "all_scores": null,
      "model_name": "canstralian/WhiteRabbitNeo",
      "timestamp": "2024-01-01T12:00:00",
      "processing_time_ms": null
    },
    {
      "code": "print('Hello World')",
      "label": "BENIGN",
      "score": 0.97,
      "all_scores": null,
      "model_name": "canstralian/WhiteRabbitNeo",
      "timestamp": "2024-01-01T12:00:00",
      "processing_time_ms": null
    }
  ],
  "total_processed": 3,
  "total_time_ms": 234.56,
  "avg_time_per_item_ms": 78.19
}
```

**Constraints:**
- Maximum batch size: 32 (configurable via `MAX_BATCH_SIZE`)
- All code snippets must be non-empty

**Status Codes:**
- `200` - Success
- `400` - Invalid request
- `404` - Batch classification disabled
- `422` - Validation error (batch too large, empty codes)
- `429` - Rate limit exceeded
- `500` - Classification error

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "codes": [
      "def test(): pass",
      "import os; os.system(\"cmd\")"
    ]
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/batch",
    json={
        "codes": [
            "def safe_function(): return True",
            "eval(user_input)",
            "subprocess.Popen(shell=True)"
        ],
        "return_all_scores": True
    }
)

data = response.json()
for result in data["results"]:
    print(f"{result['label']}: {result['score']:.2%}")
```

---

### 5. Model Information

**GET /model/info** - Get information about loaded models

**Query Parameters:**
- `model_name` (optional) - Specific model to query

**Response:**
```json
{
  "model_name": "canstralian/WhiteRabbitNeo",
  "cached": true,
  "device": "CPU",
  "max_length": 512,
  "cache_size": 1,
  "gpu_available": false
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/model/info"
curl "http://localhost:8000/model/info?model_name=canstralian/RabbitRedux"
```

---

### 6. Clear Model Cache

**POST /model/clear-cache** - Clear cached models from memory

**Headers:**
```
X-API-Key: your-api-key-here  // Required if authentication enabled
```

**Response:**
```json
{
  "status": "success",
  "message": "Model cache cleared"
}
```

**Status Codes:**
- `200` - Cache cleared
- `401` - API key required
- `403` - Invalid API key
- `500` - Failed to clear cache

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/model/clear-cache" \
  -H "X-API-Key: your-api-key-here"
```

---

### 7. Prometheus Metrics

**GET /metrics** - Prometheus-format metrics for monitoring

**Response:** (text/plain)
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",path="/classify",status="200"} 1234

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1",path="/classify"} 950
...
```

---

## Authentication

When `REQUIRE_API_KEY=true` in environment:

**All requests require:**
```
X-API-Key: your-api-key-here
```

**Example:**
```bash
curl -X POST "http://localhost:8000/classify" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"code": "test"}'
```

**Responses:**
- `401` - API key missing
- `403` - Invalid API key

---

## Rate Limiting

**Default Limits:**
- 60 requests per minute per IP/API key

**Response when exceeded:**
```json
{
  "detail": "Rate limit exceeded. Maximum 60 requests per minute."
}
```

**Status Code:** `429 Too Many Requests`

---

## Environment Configuration

Create `.env` file (see `.env.example`):

```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Security
REQUIRE_API_KEY=true
API_KEY=your-secure-api-key

# Model
DEFAULT_MODEL=canstralian/WhiteRabbitNeo
ENABLE_GPU=true

# Features
ENABLE_BATCH_CLASSIFICATION=true
ENABLE_MODEL_VERSIONING=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Monitoring
ENABLE_METRICS=true
```

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

**Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

*(Disabled in production by default)*

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "error_type": "ExceptionName",  // Optional
  "timestamp": "2024-01-01T12:00:00"  // Optional
}
```

**Common Error Codes:**
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing auth)
- `403` - Forbidden (invalid auth)
- `404` - Not Found (endpoint disabled)
- `422` - Validation Error (invalid data format)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error
- `503` - Service Unavailable (model not loaded)

---

## Performance Tips

1. **Use Batch Classification:** Process multiple codes in one request for better throughput
2. **Enable GPU:** Set `ENABLE_GPU=true` for 3-5x faster inference
3. **Model Caching:** First request loads model, subsequent requests are faster
4. **Increase Workers:** Use more Uvicorn workers for concurrent requests: `--workers 8`
5. **Async Requests:** Use async HTTP clients for parallel classification requests

**Python Async Example:**
```python
import asyncio
import httpx

async def classify_codes(codes):
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(
                "http://localhost:8000/classify",
                json={"code": code}
            )
            for code in codes
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

# Run
codes = ["code1", "code2", "code3"]
results = asyncio.run(classify_codes(codes))
```

---

## Model Versioning

Specify different models or versions:

```json
{
  "code": "test",
  "model_name": "canstralian/RabbitRedux",
  "model_version": "v2.0"
}
```

**Available Models:**
- `canstralian/WhiteRabbitNeo` (default)
- `canstralian/RabbitRedux`
- Any HuggingFace text-classification model

---

## Monitoring with Prometheus

**Grafana Dashboard:**

1. Add Prometheus data source: `http://localhost:9090`
2. Import metrics from: `http://localhost:8000/metrics`
3. Track:
   - Request rate
   - Response times
   - Error rates
   - Model inference time

---

## Support

- **Repository:** https://github.com/canstralian/RabbitRedux
- **Issues:** https://github.com/canstralian/RabbitRedux/issues
- **Author:** Stephen de Jager (@canstralian)
- **License:** Apache 2.0
