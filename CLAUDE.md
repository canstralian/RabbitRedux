# CLAUDE.md - AI Assistant Guide for RabbitRedux

## Project Overview

**RabbitRedux** is a transformer-based AI model designed for **code classification** in **cybersecurity** and **software engineering** contexts. The project includes:

- A fine-tuned transformer model (based on WhiteRabbitNeo) for classifying code snippets
- Flask REST API for programmatic access
- Gradio web interface for interactive classification
- Comprehensive training pipeline with multiple optimization strategies
- Docker deployment configuration
- CI/CD workflows for testing, linting, and HuggingFace deployment

### Key Metrics
- **Accuracy**: 94.5%
- **F1 Score**: 92.8%
- **License**: Apache 2.0
- **Model Hub**: `canstralian/RabbitRedux`

---

## Repository Structure

```
RabbitRedux/
├── .github/                          # GitHub configuration
│   ├── workflows/                    # CI/CD workflows
│   │   ├── ci.yml                   # Main CI pipeline
│   │   ├── python-app.yml           # Python testing workflow
│   │   ├── linting.yml              # Code quality checks
│   │   ├── huggingface_deploy.yml   # Model deployment
│   │   └── huggingface-login.yml    # HF authentication
│   ├── ISSUE_TEMPLATE/              # Bug/feature templates
│   ├── CODE_OF_CONDUCT.md
│   └── CONTRIBUTING.md
│
├── app/                              # Flask application package
│   ├── __init__.py                  # Factory pattern: create_app()
│   ├── config.py                    # Configuration (DEBUG, SECRET_KEY)
│   ├── routes.py                    # API endpoints (/, /classify)
│   └── model.py                     # Model loading logic
│
├── experiments/                      # Training experiments
│   ├── train_adamw.py               # AdamW optimizer
│   ├── train_swa.py                 # Stochastic Weight Averaging
│   ├── train_mixed_precision.py     # FP16 training
│   └── train_lr_scheduler.py        # Learning rate scheduling
│
├── tests/                            # Test suite
│   └── test_api.py                  # API endpoint tests (4 test cases)
│
├── app.py                            # Simplified Flask entry point
├── classifier.py                     # Model wrapper
├── interface.py                      # Gradio UI (port 7860)
├── train.py                          # Generic training script
├── train_rabbitredux.py              # Production training pipeline
├── fine_tune_multi_datasets.py       # Multi-dataset fine-tuning
├── wsgi.py                           # WSGI entry for production
├── Dockerfile                        # Docker configuration
├── requirements.txt                  # Python dependencies
├── .gitingnore                       # Git ignore (misspelled, should be .gitignore)
├── LICENSE.md
└── README.md
```

---

## Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **ML Framework** | PyTorch | Deep learning backend |
| **NLP** | HuggingFace Transformers | Pre-trained models and training |
| **Web Framework** | Flask | REST API server |
| **WSGI Server** | Gunicorn | Production deployment |
| **UI Framework** | Gradio | Interactive web interface |
| **Testing** | pytest | Unit and integration testing |
| **Linting** | flake8, pylint | Code quality enforcement |
| **Model Hub** | HuggingFace Hub | Model versioning |
| **Containerization** | Docker | Reproducible deployment |
| **CI/CD** | GitHub Actions | Automated workflows |

---

## Development Workflows

### 1. Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/canstralian/RabbitRedux.git
cd RabbitRedux

# Install dependencies
pip install -r requirements.txt

# Additional dev dependencies
pip install pytest flake8 pylint
```

### 2. Running the Application

#### Flask API (Development)
```bash
python app.py
# Runs on http://localhost:5000
```

#### Flask API (Production)
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

#### Gradio Interface
```bash
python interface.py
# Runs on http://localhost:7860
```

#### Docker Deployment
```bash
docker build -t rabbitredux .
docker run -p 5000:5000 rabbitredux
```

### 3. Testing Workflow

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=app tests/
```

**Test Files**: `tests/test_api.py`
- `test_home_endpoint`: Validates GET / endpoint
- `test_classify_endpoint_valid`: Tests POST /classify with valid input
- `test_classify_endpoint_missing_code`: Tests error handling
- `test_classify_endpoint_invalid_json`: Tests invalid JSON handling

### 4. Code Quality Checks

```bash
# Flake8 linting (enforced in CI)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Pylint
pylint app/ tests/
```

### 5. Training Workflows

#### Basic Training
```bash
python train.py
```

#### Production Training (Recommended)
```bash
python train_rabbitredux.py
```

**Features**:
- Mixed precision training (FP16)
- Gradient accumulation (steps=2)
- Data augmentation (variable renaming, formatting changes)
- L1 unstructured pruning (20% of weights)
- Multi-dataset loading (5 datasets)

#### Experimental Training
```bash
# AdamW optimizer
python experiments/train_adamw.py

# Stochastic Weight Averaging
python experiments/train_swa.py

# Mixed precision
python experiments/train_mixed_precision.py

# Cosine annealing scheduler
python experiments/train_ir_scheduler.py
```

### 6. CI/CD Workflows

All workflows trigger on `push` and `pull_request` to `main` branch:

- **ci.yml**: Runs tests and linting
- **python-app.yml**: Primary workflow (Python 3.10, pytest, flake8)
- **linting.yml**: Dedicated linting checks
- **huggingface_deploy.yml**: Deploys to HuggingFace Hub (requires `HF_TOKEN` secret)

---

## API Endpoints

### GET `/`
Returns project metadata.

**Response**:
```json
{
  "project": "RabbitRedux - WhiteRabbitNeo Code Classification Model",
  "description": "A Transformer-based model designed for text classification of code snippets.",
  "repository": "https://github.com/canstralian/WhiteRabbitNeo",
  "author": "Stephen de Jager (canstralian)",
  "license": "Apache 2.0"
}
```

### POST `/classify`
Classifies a code snippet.

**Request**:
```json
{
  "code": "def hello_world():\n    print('Hello, world!')"
}
```

**Response**:
```json
{
  "code": "def hello_world():\n    print('Hello, world!')",
  "classification": [
    {
      "label": "Python Function",
      "score": 0.98
    }
  ]
}
```

**Error Responses**:
- `400`: Missing 'code' field
- `500`: Internal server error

---

## Key Conventions and Patterns

### 1. Flask Application Factory Pattern

The app uses the **factory pattern** for Flask initialization:

```python
# app/__init__.py
def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config")
    configure_routes(app)
    return app
```

**Benefits**:
- Enables testing with different configurations
- Separation of concerns
- WSGI-compatible

### 2. Model Loading Pattern

Models are loaded once at startup (singleton-like pattern):

```python
# app/routes.py
from app.model import classifier
model = classifier  # Load once, reuse for all requests
```

**Important**: The model is loaded from HuggingFace Hub at runtime.

### 3. Error Handling

All API endpoints follow this pattern:
- Validate input
- Log errors using Python's `logging` module
- Return appropriate HTTP status codes
- Provide descriptive error messages

### 4. Configuration Management

Environment-based configuration:
```python
# app/config.py
DEBUG = os.getenv("FLASK_DEBUG", False)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable must be set and non-empty")
```

### 5. Training Best Practices

**Data Augmentation** (train_rabbitredux.py):
- Variable renaming
- Formatting changes (tabs ↔ spaces)
- Comment manipulation
- 50% probability application

**Optimization Strategies**:
- Mixed precision (FP16) for memory efficiency
- Gradient accumulation for larger effective batch sizes
- Model pruning for inference speed
- Learning rate scheduling (cosine annealing)

---

## Common Tasks for AI Assistants

### Adding a New API Endpoint

1. **Add route in `app/routes.py`**:
   ```python
   @app.route('/new-endpoint', methods=['POST'])
   def new_endpoint():
       # Implementation
       return jsonify({"result": "success"})
   ```

2. **Register route if using factory pattern**:
   - Routes are auto-configured via `configure_routes(app)` in `app/__init__.py`

3. **Add tests in `tests/test_api.py`**:
   ```python
   def test_new_endpoint(client):
       response = client.post('/new-endpoint', json={"key": "value"})
       assert response.status_code == 200
   ```

4. **Run tests**: `pytest tests/test_api.py`

### Modifying the Model

1. **Update model reference in `classifier.py`** or `app/model.py`
2. **Update model name in training scripts** (`train_rabbitredux.py`)
3. **Update HuggingFace deployment workflow** (`.github/workflows/huggingface_deploy.yml`)
4. **Update README.md** with new model details

### Adding New Training Features

1. **Create new script in `experiments/`** for experimental features
2. **Update `train_rabbitredux.py`** for production features
3. **Document in README.md** if significant improvement
4. **Add metrics tracking** using `compute_metrics()` function

### Fixing Linting Issues

```bash
# Check issues
flake8 .

# Common fixes
# - Line length: max 127 characters
# - Unused imports: remove them
# - Undefined names: fix imports
# - Indentation: 4 spaces (PEP 8)
```

### Updating Dependencies

1. **Update `requirements.txt`**
2. **Test locally**: `pip install -r requirements.txt`
3. **Run full test suite**: `pytest tests/`
4. **Verify CI passes** before merging

---

## Important Notes for AI Assistants

### File System Quirks

- **Typo Alert**: `.gitingnore` should be `.gitignore` (consider fixing this)
- **No `package.json`**: This is a Python project, not Node.js

### Model References

The codebase references multiple model names:
- `canstralian/RabbitRedux` (in README.md)
- `canstralian/WhiteRabbitNeo` (in routes.py, classifier.py)

**Action Required**: Verify which model is the canonical version.

### Training Datasets

The project uses 5 datasets:
1. WhiteRabbitNeo/WRN-Chapter-1
2. WhiteRabbitNeo/WRN-Chapter-2
3. WhiteRabbitNeo/Code-Functions-Level-General
4. WhiteRabbitNeo/Code-Functions-Level-Cyber
5. replit/agent-challenge

### Environment Variables

Required for production:
- `FLASK_DEBUG`: Set to `False` in production
- `SECRET_KEY`: Strong random key for session management
- `HF_TOKEN`: HuggingFace API token for deployment

### Testing Requirements

- All new features must include tests in `tests/test_api.py`
- Tests must pass before PR approval
- Minimum coverage: Aim for >80% coverage on critical paths

### Code Style Guidelines

From `.github/CONTRIBUTING.md`:
- Follow existing code style and conventions
- Write clear and concise comments where necessary
- Use descriptive variable names
- Keep functions focused and single-purpose

### Git Workflow

Standard fork → branch → PR workflow:
1. Fork the repository
2. Create a feature branch
3. Make changes with clear commit messages
4. Submit PR against main repository

### Deployment Checklist

Before deploying:
- [ ] All tests pass (`pytest tests/`)
- [ ] Linting passes (`flake8 .`)
- [ ] README.md updated if needed
- [ ] Environment variables configured
- [ ] Docker image builds successfully
- [ ] Model is accessible from HuggingFace Hub

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'app.model'`
- **Solution**: Ensure `app/model.py` exists or update import in `routes.py`

**Issue**: Model loading timeout
- **Solution**: Check HuggingFace Hub status, verify model name, check internet connection

**Issue**: Tests fail in CI but pass locally
- **Solution**: Check Python version (CI uses 3.10), verify all dependencies in `requirements.txt`

**Issue**: Docker container won't start
- **Solution**: Check logs with `docker logs <container_id>`, verify port 5000 is available

**Issue**: Gradio interface can't connect to Flask API
- **Solution**: Ensure Flask is running on port 5000, check `interface.py` API endpoint URL

---

## Performance Optimization

### Inference Optimization

- Model is loaded once at startup (not per request)
- Use mixed precision (FP16) for faster inference
- Consider model quantization for production (INT8)
- Batch predictions when possible

### Training Optimization

Current optimizations in `train_rabbitredux.py`:
- Mixed precision training (reduces memory by ~50%)
- Gradient accumulation (effective batch size × 2)
- Model pruning (20% weight reduction)
- Efficient data loading with HuggingFace datasets

### API Optimization

- Use Gunicorn with multiple workers: `gunicorn -w 4 wsgi:app`
- Add caching for repeated predictions
- Consider async processing for long-running requests
- Implement request queuing for high load

---

## Security Considerations

### Current Security Measures

- Secret key management via environment variables
- Input validation on `/classify` endpoint
- Error handling without exposing stack traces
- Apache 2.0 license compliance

### Recommendations for AI Assistants

When modifying code:
- **Never expose secrets** in code or logs
- **Validate all user inputs** before processing
- **Sanitize error messages** sent to clients
- **Use HTTPS** in production
- **Implement rate limiting** for API endpoints
- **Add authentication** for sensitive operations

---

## Additional Resources

- **GitHub Repository**: https://github.com/canstralian/RabbitRedux
- **HuggingFace Model**: https://huggingface.co/canstralian/RabbitRedux
- **Replit Profile**: https://replit.com/@canstralian
- **Issue Templates**: `.github/ISSUE_TEMPLATE/`
- **Contributing Guidelines**: `.github/CONTRIBUTING.md`

---

## Quick Reference Commands

```bash
# Development
python app.py                          # Run Flask API (dev)
python interface.py                    # Run Gradio UI

# Testing
pytest tests/                          # Run all tests
pytest -v tests/test_api.py           # Run specific test

# Linting
flake8 .                              # Check code quality
pylint app/ tests/                    # Advanced linting

# Training
python train_rabbitredux.py           # Production training
python experiments/train_swa.py       # Experimental training

# Production
gunicorn --bind 0.0.0.0:5000 wsgi:app # Run with Gunicorn
docker build -t rabbitredux .         # Build Docker image
docker run -p 5000:5000 rabbitredux  # Run container

# Git
git checkout -b feature/my-feature    # Create feature branch
git push -u origin feature/my-feature # Push to remote
```

---

**Last Updated**: 2025-12-31
**Maintained by**: Stephen de Jager (canstralian)
**For AI Assistants**: This document is specifically designed to help AI coding assistants understand the RabbitRedux codebase quickly and work effectively within established conventions.
