from flask import Flask, request, jsonify
import logging
import sys
import os

# Add parent directory to path to import classifier
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from classifier import load_classifier, classify_code

app = Flask(__name__)

# ----- Setup Logging -----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----- Load Model Once -----
try:
    model = load_classifier()
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

def configure_routes(app):
    """Configure Flask routes."""
    
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
        if model is None:
            logger.error("Model not loaded")
            return jsonify({"error": "Model not available"}), 503
        
        data = request.get_json()

        if not data or "code" not in data:
            logger.error("Missing 'code' field in request")
            return jsonify({"error": "Missing 'code' field in request"}), 400

        code_snippet = data["code"]
        try:
            result = classify_code(model, code_snippet)
            return jsonify({"code": code_snippet, "classification": result})
        except Exception as e:
            logger.error(f"Error during classification: {e}")
            return jsonify({"error": "Internal server error"}), 500