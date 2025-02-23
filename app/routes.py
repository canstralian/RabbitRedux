from flask import Flask, request, jsonify
from app.model import classifier
import logging

app = Flask(__name__)

# ----- Setup Logging -----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----- Load Model Once -----
model = classifier  # Load your model here

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
def classify_code():
    """API endpoint to classify code snippets."""
    data = request.get_json()

    if not data or "code" not in data:
        logger.error("Missing 'code' field in request")
        return jsonify({"error": "Missing 'code' field in request"}), 400

    code_snippet = data["code"]
    try:
        result = model(code_snippet)
        return jsonify({"code": code_snippet, "classification": result})
    except Exception as e:
        logger.error(f"Error during classification: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)