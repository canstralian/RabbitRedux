from flask import Flask, request, jsonify
from classifier import load_classifier, classify_code

app = Flask(__name__)

# Load the classifier once at startup
classifier = load_classifier()

@app.route('/')
def home():
    """Root endpoint displaying project information."""
    return jsonify({
        "project": "RabbitRedux - WhiteRabbitNeo Code Classification Model",
        "description": "A Transformer-based model designed for text classification of code snippets.",
        "repository": "https://github.com/canstralian/WhiteRabbitNeo",
        "author": "Stephen de Jager (canstralian)",
        "license": "Apache 2.0"
    })

@app.route('/classify', methods=['POST'])
def classify_code_endpoint():
    """API endpoint to classify code snippets."""
    data = request.get_json()
    
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in request"}), 400

    code_snippet = data["code"]
    result = classify_code(classifier, code_snippet)

    return jsonify({"code": code_snippet, "classification": result})