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

## 🚀 Usage

### **1️⃣ Install Dependencies**
```sh
pip install transformers torch
```

### **2️⃣ Load the Model**
```python
from transformers import pipeline

# Load RabbitRedux
classifier = pipeline("text-classification", model="canstralian/RabbitRedux")

# Example classification
code_snippet = "def hello_world():\n    print('Hello, world!')"
result = classifier(code_snippet)
print(result)
```

### **3️⃣ Example Output**
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

You can deploy this model as an API using Hugging Face Spaces.

### **Deploy with Docker**
```sh
docker build -t rabbitredux .
docker run -p 5000:5000 rabbitredux
```

### **Use with FastAPI**
If you want a scalable API:

```sh
pip install fastapi uvicorn
```

Then, create a FastAPI server:

```python
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()
classifier = pipeline("text-classification", model="canstralian/RabbitRedux")

@app.post("/classify/")
def classify_code(data: dict):
    return {"classification": classifier(data["code"])}
```

Run with:

```sh
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## 📚 Useful Resources
   • **GitHub**: [canstralian](https://github.com/canstralian)  
   • **Hugging Face Model**: [RabbitRedux](https://huggingface.co/canstralian/RabbitRedux)  
   • **Replit Profile**: [canstralian](https://replit.com/@canstralian)  

---

## 📜 License

Licensed under the **MIT License**.
