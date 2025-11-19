# RabbitRedux Quick Start Guide

Get RabbitRedux up and running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- pip
- Docker (optional, for containerized deployment)

## Option 1: Quick Start with Python

### 1. Clone and Setup

```bash
git clone https://github.com/canstralian/RabbitRedux.git
cd RabbitRedux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### 4. Test It Out

Open another terminal and try:

```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): print(\"Hello, world!\")"}'
```

## Option 2: Quick Start with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/canstralian/RabbitRedux.git
cd RabbitRedux
```

### 2. Build and Run

```bash
docker-compose up -d
```

### 3. Test It Out

```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): print(\"Hello, world!\")"}'
```

## Option 3: Using Make Commands

If you have `make` installed:

```bash
# Install dependencies
make install

# Run development server
make run

# Or run with Gunicorn (production-like)
make run-prod
```

## Testing the API

### Check Health

```bash
curl http://localhost:5000/health
```

### Get API Info

```bash
curl http://localhost:5000/
```

### Classify Code

Python example:
```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"}'
```

JavaScript example:
```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"code": "function add(a, b) { return a + b; }"}'
```

## Using the API in Your Code

### Python

```python
import requests

response = requests.post(
    'http://localhost:5000/classify',
    json={'code': 'def hello(): print("Hello!")'}
)

result = response.json()
print(result['classification'])
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

axios.post('http://localhost:5000/classify', {
  code: 'function hello() { console.log("Hello!"); }'
})
.then(response => {
  console.log(response.data.classification);
})
.catch(error => {
  console.error(error);
});
```

### cURL

```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, world!\")"}'
```

## Development Setup

For development with hot-reload and testing:

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Run with coverage
make test-cov

# Lint code
make lint

# Format code
make format
```

## Next Steps

- 📖 Read the [API Documentation](API.md) for detailed endpoint information
- 🚀 Check the [Deployment Guide](DEPLOYMENT.md) for production deployment
- 🔒 Review [Security Best Practices](SECURITY.md)
- 📋 Use the [Production Checklist](PRODUCTION_CHECKLIST.md) before going live

## Common Issues

### Model Download Takes Too Long

The first time you run the application, it needs to download the model from Hugging Face. This can take several minutes depending on your internet connection. The model is cached for subsequent runs.

### Port Already in Use

If port 5000 is already in use, you can change it:

```bash
# For Python
FLASK_RUN_PORT=8000 python app.py

# For Docker
docker run -p 8000:5000 rabbitredux
```

### Memory Issues

The model requires at least 4GB of RAM. If you're running out of memory:

1. Close other applications
2. Reduce the number of Gunicorn workers
3. Use a machine with more RAM

### Network Issues

If you can't download the model from Hugging Face:

1. Check your internet connection
2. Verify you can access huggingface.co
3. Check firewall settings
4. Consider using a VPN if behind a restrictive network

## Getting Help

- 📝 [GitHub Issues](https://github.com/canstralian/RabbitRedux/issues)
- 📧 Email the maintainer (see repository)
- 💬 Check existing issues for solutions

## What's Next?

After getting it running locally, you might want to:

1. **Deploy to Production**: Follow the [deployment guide](DEPLOYMENT.md)
2. **Customize**: Modify the code to fit your needs
3. **Integrate**: Use the API in your applications
4. **Contribute**: Submit improvements via pull requests

Enjoy using RabbitRedux! 🐇
