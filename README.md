# 🐇 RabbitRedux - Production-Ready Code Classification API

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)](https://fastapi.tiangolo.com/)
[![HuggingFace](https://img.shields.io/badge/🤗-Models-yellow.svg)](https://huggingface.co/canstralian/RabbitRedux)

**Production-ready ML API for cybersecurity-focused code classification using transformer models.**

---

## 🔍 Overview

RabbitRedux is a **transformer-based AI system** for classifying code snippets, with specialized focus on **cybersecurity** and **software engineering** applications. It provides both REST APIs (FastAPI & Flask) for easy integration into security tools, CI/CD pipelines, and code analysis workflows.

### ✨ Key Features

- 🚀 **FastAPI** + **Flask** APIs (production & legacy support)
- 🔐 **API Key Authentication** & **Rate Limiting**
- 📊 **Prometheus Metrics** for monitoring
- 🎯 **Batch Classification** for high throughput
- 🏷️ **Model Versioning** support
- 🐳 **Docker** deployment ready
- 📚 **Auto-generated OpenAPI** documentation
- ⚡ **GPU Acceleration** support
- 🔄 **Model Caching** for performance
- 🧪 **Comprehensive Test Suite**

### 🎯 Use Cases

- **Security Code Review** - Identify potentially dangerous code patterns
- **Malware Detection** - Classify code behavior (benign vs. malicious)
- **Code Categorization** - Organize code by function/domain
- **CI/CD Integration** - Automated security scanning
- **Educational Tools** - Code analysis for learning cybersecurity

---

## 📊 Model Performance

| Metric     | Value  |
|------------|--------|
| Accuracy   | 94.5%  |
| F1 Score   | 92.8%  |
| Max Tokens | 512    |
| Device     | CPU/GPU |

**Supported Languages:** Python, JavaScript, Shell Scripts, and more

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/canstralian/RabbitRedux.git
cd RabbitRedux

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env with your settings
nano .env
```

### Running the API

#### Option 1: FastAPI (Recommended)

```bash
# Development with auto-reload
uvicorn main:app --reload

# Production with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Option 2: Flask (Legacy)

```bash
# Development
python app.py

# Production with Gunicorn
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 4
```

#### Option 3: Docker

```bash
# Build image
docker build -t rabbitredux .

# Run container (FastAPI)
docker run -p 8000:8000 rabbitredux

# Run container (Flask)
docker run -p 5000:5000 rabbitredux gunicorn --bind 0.0.0.0:5000 wsgi:app
```

---

## 💻 Usage Examples

### Python SDK

```python
from transformers import pipeline

# Load model
classifier = pipeline("text-classification", model="canstralian/WhiteRabbitNeo")

# Classify code
code = """
import os
os.system('whoami')
"""

result = classifier(code)
print(result)
# [{'label': 'SECURITY', 'score': 0.95}]
```

### REST API

#### Single Classification

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import subprocess; subprocess.call([\"ls\", \"-la\"])"
  }'
```

**Response:**
```json
{
  "label": "SECURITY",
  "score": 0.95,
  "code": "import subprocess; subprocess.call([\"ls\", \"-la\"])",
  "model_name": "canstralian/WhiteRabbitNeo",
  "timestamp": "2024-01-01T12:00:00",
  "processing_time_ms": 123.45
}
```

#### Batch Classification

```bash
curl -X POST "http://localhost:8000/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "codes": [
      "def add(a, b): return a + b",
      "eval(user_input)",
      "print(\"Hello World\")"
    ]
  }'
```

**Response:**
```json
{
  "results": [
    {"label": "BENIGN", "score": 0.98, "code": "def add(a, b): return a + b"},
    {"label": "SECURITY", "score": 0.97, "code": "eval(user_input)"},
    {"label": "BENIGN", "score": 0.99, "code": "print(\"Hello World\")"}
  ],
  "total_processed": 3,
  "total_time_ms": 234.56,
  "avg_time_per_item_ms": 78.19
}
```

#### With Authentication

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"code": "test"}'
```

### Python Requests

```python
import requests

# Single classification
response = requests.post(
    "http://localhost:8000/classify",
    json={"code": "import os; os.system('cmd')"}
)
print(response.json())

# Batch classification
response = requests.post(
    "http://localhost:8000/batch",
    json={
        "codes": [
            "def safe(): pass",
            "eval(user_data)",
            "exec(malicious_code)"
        ],
        "return_all_scores": True
    }
)
results = response.json()
for item in results["results"]:
    print(f"{item['label']}: {item['score']:.2%}")
```

---

## 📚 API Documentation

### Interactive Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Full API Reference

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete endpoint documentation, examples, and integration guides.

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/classify` | POST | Classify single code snippet |
| `/batch` | POST | Batch classification |
| `/model/info` | GET | Model information |
| `/model/clear-cache` | POST | Clear model cache |
| `/metrics` | GET | Prometheus metrics |

---

## ⚙️ Configuration

Create `.env` file from template:

```bash
cp .env.example .env
```

### Key Settings

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production

# Security
REQUIRE_API_KEY=true
API_KEY=your-secure-key-here
SECRET_KEY=your-secret-key

# Model
DEFAULT_MODEL=canstralian/WhiteRabbitNeo
ENABLE_GPU=true
MAX_MODEL_LENGTH=512

# Features
ENABLE_BATCH_CLASSIFICATION=true
ENABLE_MODEL_VERSIONING=true
ENABLE_METRICS=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Performance
MAX_BATCH_SIZE=32
API_WORKERS=4
```

See [.env.example](.env.example) for all available options.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_fastapi.py -v

# Run with output
pytest -s
```

### Test Coverage

- ✅ All API endpoints
- ✅ Authentication & authorization
- ✅ Rate limiting
- ✅ Error handling
- ✅ Model loading & caching
- ✅ Batch processing
- ✅ Model versioning

---

## 🔧 Development

### Code Quality

```bash
# Linting
flake8 . --max-line-length=120 --exclude=venv,__pycache__

# Code formatting
black . --line-length=120

# Type checking
mypy main.py --ignore-missing-imports

# Import sorting
isort . --profile black
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📦 Model Training

Train custom models using included scripts:

```bash
# Basic training
python train.py

# Advanced training with pruning
python train_rabbitredux.py

# Multi-dataset fine-tuning
python fine_tune_multi_datasets.py

# Experimental optimizations
python experiments/train_swa.py
```

### Deploy to HuggingFace

```bash
python deploy_to_huggingface.py \
  --model-path ./trained_model \
  --repo-id canstralian/MyModel \
  --accuracy 0.95 \
  --f1-score 0.92
```

Or use GitHub Actions workflow (manual trigger).

---

## 📊 Monitoring

### Prometheus Metrics

Metrics available at: http://localhost:8000/metrics

**Key Metrics:**
- `http_requests_total` - Total requests
- `http_request_duration_seconds` - Request latency
- `http_requests_in_progress` - Active requests
- `model_inference_time_seconds` - Model processing time

### Grafana Dashboard

1. Add Prometheus data source
2. Import RabbitRedux dashboard (coming soon)
3. Monitor performance in real-time

---

## 🏗️ Architecture

### Project Structure

```
RabbitRedux/
├── main.py                 # FastAPI application (production)
├── app.py                  # Flask application (legacy)
├── config.py               # Configuration management
├── classifier.py           # Model utilities (legacy)
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── routes.py          # Flask routes
│   ├── model.py           # Model loading & inference
│   └── config.py          # Flask config
├── tests/
│   ├── test_fastapi.py    # FastAPI tests
│   └── test_api.py        # Flask tests
├── experiments/           # Training experiments
├── .github/workflows/     # CI/CD pipelines
├── Dockerfile            # Multi-stage Docker build
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── API_DOCUMENTATION.md # Full API docs
```

### Technology Stack

- **Frameworks:** FastAPI, Flask
- **ML:** HuggingFace Transformers, PyTorch
- **API:** Uvicorn, Gunicorn
- **Testing:** pytest, httpx
- **Monitoring:** Prometheus
- **Deployment:** Docker, GitHub Actions
- **Code Quality:** flake8, pylint, black, mypy

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines.

---

## 📋 Datasets

Training datasets:

- **WhiteRabbitNeo/WRN-Chapter-1** - Cybersecurity code patterns
- **WhiteRabbitNeo/WRN-Chapter-2** - Advanced exploit code
- **WhiteRabbitNeo/Code-Functions-Level-Cyber** - Function-level classification
- **WhiteRabbitNeo/Code-Functions-Level-General** - General code
- **Canstralian/CyberExploitDB** - Exploit database
- **Canstralian/pentesting_dataset** - Penetration testing code
- **replit/agent-challenge** - Code generation dataset

---

## 📝 License

Licensed under the **Apache License 2.0** - see [LICENSE.md](LICENSE.md)

---

## 👤 Author

**Stephen de Jager (canstralian)**

- GitHub: [@canstralian](https://github.com/canstralian)
- HuggingFace: [@canstralian](https://huggingface.co/canstralian)
- Email: [Contact via GitHub]

---

## 🌟 Acknowledgments

- HuggingFace for transformer infrastructure
- WhiteRabbitNeo project for cybersecurity datasets
- FastAPI for excellent API framework
- All contributors and users

---

## 📈 Roadmap

- [ ] ONNX model export for faster inference
- [ ] Quantization for reduced model size
- [ ] Multi-language support (Java, C++, Go)
- [ ] Fine-grained classification categories
- [ ] Real-time streaming classification
- [ ] Web UI dashboard
- [ ] Kubernetes deployment manifests
- [ ] Model explanation/interpretability
- [ ] Active learning for model improvement

---

## 🐛 Issues & Support

- **Bug Reports:** [GitHub Issues](https://github.com/canstralian/RabbitRedux/issues)
- **Feature Requests:** [GitHub Discussions](https://github.com/canstralian/RabbitRedux/discussions)
- **Security:** Report via email or GitHub Security tab

---

## 📖 Citation

If you use RabbitRedux in your research:

```bibtex
@software{rabbitredux2024,
  author = {de Jager, Stephen},
  title = {RabbitRedux: Code Classification for Cybersecurity},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/canstralian/RabbitRedux}
}
```

---

**⭐ Star this repo if you find it useful!**
