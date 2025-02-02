---
language: 
  - en
tags: 
  - code-classification
  - cybersecurity
  - machine-learning
  - transformers
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

# 🐇 RabbitRedux API - WhiteRabbitNeo Code Classification

![Build Status](https://img.shields.io/github/actions/workflow/status/canstralian/RabbitRedux/ci.yml)
![Coverage Status](https://img.shields.io/codecov/c/github/canstralian/RabbitRedux)
![License](https://img.shields.io/github/license/canstralian/RabbitRedux)

## 🚀 Overview
RabbitRedux is a Flask-based API that serves **WhiteRabbitNeo**, a **Transformer-based model** designed for **code classification** in cybersecurity and software engineering.

### 🌟 Features
- **Text Classification API**: Classifies code snippets.
- **Fast & Scalable**: Runs with **Gunicorn** inside a **Docker container**.
- **AI-Powered**: Uses **Hugging Face Transformers**.

---

## 🛠️ Installation & Usage

### **1️⃣ Clone Repository**
```sh
git clone https://github.com/canstralian/RabbitRedux.git
cd RabbitRedux

2️⃣ Install Dependencies

pip install -r requirements.txt

3️⃣ Run Locally

python wsgi.py

Visit http://localhost:5000 to test the API.

4️⃣ Run with Docker

docker build -t rabbitredux .
docker run -p 5000:5000 rabbitredux

🔥 API Endpoints

Method	Endpoint	Description
GET	/	Get project details
POST	/classify	Classify a code snippet

Example Request

curl -X POST "http://localhost:5000/classify" -H "Content-Type: application/json" -d '{"code": "def hello(): print(\"Hello, world!\")"}'

Example Response

{
  "code": "def hello(): print(\"Hello, world!\")",
  "classification": [{"label": "Python Function", "score": 0.98}]
}

📚 Useful Resources
   •   GitHub: canstralian
   •   Replit: canstralian

📜 License

Licensed under the Apache 2.0 License.

---



