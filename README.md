---
language: 
  - en
tags: 
  - code-classification
  - cybersecurity
  - transformers
  - machine-learning
  - huggingface
license: apache-2.0
library_name: transformers
datasets:
  - WhiteRabbitNeo/WRN-Chapter-1
  - WhiteRabbitNeo/WRN-Chapter-2
  - WhiteRabbitNeo/Code-Functions-Level-General
  - WhiteRabbitNeo/Code-Functions-Level-Cyber
  - replit/agent-challenge
model-index:
  - name: WhiteRabbitNeo Code Classification Model
    results:
      - task:
          type: text-classification
        dataset:
          name: WhiteRabbitNeo Code Classification Dataset
          type: custom
        metrics:
          - name: Accuracy
            type: accuracy
            value: 94.5%
---

# 🐇 RabbitRedux Code Classification Model

## 🔍 Overview
The **RabbitRedux Code Classification Model** is a transformer-based AI designed for **code classification** in **cybersecurity** and **software engineering** contexts.

### 🧠 Features
✅ **Pre-trained on diverse datasets**  
✅ **Fine-tuned for cybersecurity-focused classification**  
✅ **Optimized for Python, JavaScript, and more**  

---

## 🚀 Quick Start

### **Get Started in 5 Minutes**

See the [Quick Start Guide](QUICKSTART.md) for the fastest way to get RabbitRedux running!

**TL;DR:**
```sh
# Clone and install
git clone https://github.com/canstralian/RabbitRedux.git
cd RabbitRedux
pip install -r requirements.txt

# Run the server
python app.py

# Test it
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): print(\"Hello!\")"}'
```

### **Using as a Library**

You can also use the model directly in your Python code:

```python
from transformers import pipeline

# Load RabbitRedux
classifier = pipeline("text-classification", model="canstralian/RabbitRedux")

# Example classification
code_snippet = "def hello_world():\n    print('Hello, world!')"
result = classifier(code_snippet)
print(result)
```

**Example Output:**
```json
[
  {"label": "Python Function", "score": 0.98}
]
```

---

## 📊 Model Details
   • **Developed by**: canstralian  
   • **Architecture**: Transformer-based (Fine-tuned)  
   • **Training Datasets**:
     - Canstralian/Wordlists
     - Canstralian/CyberExploitDB
     - Canstralian/pentesting_dataset
     - Canstralian/ShellCommands  
   • **Fine-tuned from**:
     - replit/replit-code-v1_5-3b  
     - WhiteRabbitNeo/Llama-3.1-WhiteRabbitNeo-2-8B  
     - WhiteRabbitNeo/Llama-3.1-WhiteRabbitNeo-2-70B  
   • **License**: MIT  

## 🏆 Performance

| Metric     | Value    |
|------------|----------|
| Accuracy   | 94.5%    |
| F1 Score   | 92.8%    |

---

## 🔥 Deployment

### **Quick Start**

1. **Install dependencies**:
```sh
pip install -r requirements.txt
```

2. **Set up environment variables**:
```sh
cp .env.example .env
# Edit .env with your settings
```

3. **Run the development server**:
```sh
python app.py
```

### **Deploy with Docker**

Build and run:
```sh
docker build -t rabbitredux .
docker run -p 5000:5000 -e SECRET_KEY=your-secret-key rabbitredux
```

Or use docker-compose:
```sh
docker-compose up -d
```

### **Production Deployment with Gunicorn**

```sh
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --timeout 120 wsgi:app
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📖 Documentation

- **[API Documentation](API.md)**: Complete API reference and usage examples
- **[Deployment Guide](DEPLOYMENT.md)**: Detailed deployment instructions for various platforms
- **[Security Policy](SECURITY.md)**: Security best practices and reporting vulnerabilities
- **[Contributing Guidelines](.github/CONTRIBUTING.md)**: How to contribute to the project

## 🧪 Testing

Run the test suite:
```sh
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

## 🔒 Security

For security issues, please see [SECURITY.md](SECURITY.md) for reporting guidelines.

Key security features:
- ✅ Input validation (max 10,000 characters)
- ✅ Secure configuration management
- ✅ Health check endpoint for monitoring
- ✅ Production-ready Docker configuration
- ✅ Non-root container user

## 📚 Useful Resources
   • **GitHub**: [canstralian](https://github.com/canstralian)  
   • **Hugging Face Model**: [RabbitRedux](https://huggingface.co/canstralian/RabbitRedux)  
   • **Replit Profile**: [canstralian](https://replit.com/@canstralian)  

---

## 📜 License

Licensed under the **Apache 2.0 License**. See [LICENSE.md](LICENSE.md) for details.
