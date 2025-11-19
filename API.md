# RabbitRedux API Documentation

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, no authentication is required. For production deployments, consider implementing:
- API Key authentication
- OAuth 2.0
- JWT tokens

## Endpoints

### 1. Root Endpoint

Get information about the API.

**Endpoint**: `GET /`

**Response**:
```json
{
  "project": "RabbitRedux - WhiteRabbitNeo Code Classification Model",
  "description": "A Transformer-based model designed for text classification of code snippets.",
  "repository": "https://github.com/canstralian/WhiteRabbitNeo",
  "author": "Stephen de Jager (canstralian)",
  "license": "Apache 2.0",
  "version": "1.0.0"
}
```

**Status Codes**:
- `200 OK`: Success

---

### 2. Health Check

Check if the API is running and healthy.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "RabbitRedux API"
}
```

**Status Codes**:
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is not healthy (if implemented with actual health checks)

**Usage**:
```bash
curl http://localhost:5000/health
```

---

### 3. Classify Code

Classify a code snippet using the WhiteRabbitNeo model.

**Endpoint**: `POST /classify`

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "code": "def hello_world():\n    print('Hello, world!')"
}
```

**Parameters**:
- `code` (string, required): The code snippet to classify. Maximum 10,000 characters.

**Response**:
```json
{
  "code": "def hello_world():\n    print('Hello, world!')",
  "classification": [
    {
      "label": "Python Function",
      "score": 0.9876543210
    }
  ]
}
```

**Status Codes**:
- `200 OK`: Classification successful
- `400 Bad Request`: Missing or invalid input
- `500 Internal Server Error`: Server error during classification

**Error Response Examples**:

Missing code field:
```json
{
  "error": "Missing 'code' field in request"
}
```

Code too long:
```json
{
  "error": "Code snippet too long (max 10000 characters)"
}
```

Internal error:
```json
{
  "error": "Internal server error"
}
```

**Usage Examples**:

#### cURL
```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello_world():\n    print(\"Hello, world!\")"
  }'
```

#### Python
```python
import requests
import json

url = "http://localhost:5000/classify"
data = {
    "code": "def hello_world():\n    print('Hello, world!')"
}

response = requests.post(url, json=data)
result = response.json()
print(json.dumps(result, indent=2))
```

#### JavaScript (Node.js)
```javascript
const axios = require('axios');

const url = 'http://localhost:5000/classify';
const data = {
  code: "def hello_world():\n    print('Hello, world!')"
};

axios.post(url, data)
  .then(response => {
    console.log(JSON.stringify(response.data, null, 2));
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

#### JavaScript (Fetch API)
```javascript
fetch('http://localhost:5000/classify', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    code: "def hello_world():\n    print('Hello, world!')"
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, implement rate limiting to prevent abuse:

- Recommended: 100 requests per minute per IP
- Consider using nginx or application-level rate limiting

## Best Practices

1. **Input Validation**: Always validate code snippets before sending
2. **Error Handling**: Implement proper error handling in your client
3. **Timeouts**: Set appropriate timeouts (recommend 30-60 seconds)
4. **Retry Logic**: Implement exponential backoff for failed requests
5. **Caching**: Cache results for identical code snippets when possible

## Response Times

Expected response times:
- Health check: < 10ms
- Code classification: 100ms - 2s (depends on code length and model performance)

## Limitations

- Maximum code snippet length: 10,000 characters
- Maximum request size: 16MB
- Model supports primarily: Python, JavaScript, and other common languages
- Classification accuracy depends on code quality and similarity to training data

## Model Information

- **Model**: canstralian/WhiteRabbitNeo
- **Type**: Text Classification (Code Classification)
- **Base Architecture**: Transformer-based
- **Training Data**: Cybersecurity and software engineering datasets
- **Supported Languages**: Python, JavaScript, and more

## Versioning

API Version: 1.0.0

Future versions will be indicated in the response and may include versioned endpoints like `/v2/classify`.

## Support and Issues

- Report issues: https://github.com/canstralian/RabbitRedux/issues
- Documentation: https://github.com/canstralian/RabbitRedux
