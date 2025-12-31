"""
Flask routes for RabbitRedux (Legacy - use main.py FastAPI for production).
This module provides backward compatibility for the Flask implementation.
"""

from flask import Flask, request, jsonify, Blueprint
from app.model import load_classifier, classify_code
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
api_blueprint = Blueprint('api', __name__)

# Load model once at module level
try:
    classifier = load_classifier()
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    classifier = None


def configure_routes(app: Flask):
    """Configure routes for the Flask application (app factory pattern)."""
    # TODO: Add deprecation warnings for Flask endpoints
    # TODO: Migrate remaining Flask users to FastAPI with compatibility layer
    # TODO: Add metrics collection for Flask endpoint usage to plan sunset

    @app.route('/')
    def home():
        """Root endpoint displaying project information."""
        return jsonify({
            "project": "RabbitRedux - WhiteRabbitNeo Code Classification Model",
            "description": "A Transformer-based model designed for text classification of code snippets.",
            "repository": "https://github.com/canstralian/RabbitRedux",
            "author": "Stephen de Jager (canstralian)",
            "license": "Apache 2.0",
            "note": "This is the legacy Flask API. Consider using FastAPI (main.py) for production.",
            "endpoints": {
                "classify": "/classify",
                "health": "/health"
            }
        })

    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy" if classifier else "degraded",
            "model_loaded": classifier is not None,
            "framework": "Flask (legacy)"
        })

    @app.route('/classify', methods=['POST'])
    def classify_code_endpoint():
        """API endpoint to classify code snippets."""
        # TODO: Add request validation matching FastAPI implementation
        # TODO: Implement rate limiting for Flask endpoints
        # TODO: Add authentication support consistent with FastAPI
        if not classifier:
            logger.error("Model not loaded")
            return jsonify({"error": "Model not available"}), 503

        data = request.get_json()

        if not data or "code" not in data:
            logger.error("Missing 'code' field in request")
            return jsonify({"error": "Missing 'code' field in request"}), 400

        code_snippet = data["code"]

        try:
            result = classify_code(classifier, code_snippet)

            if "error" in result:
                logger.error(f"Classification error: {result['error']}")
                return jsonify({"error": result["error"]}), 500

            return jsonify({
                "code": code_snippet,
                "classification": {
                    "label": result["label"],
                    "score": result["score"]
                }
            })

        except Exception as e:
            logger.error(f"Error during classification: {e}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

    return app


# Standalone Flask app (for backward compatibility)
app = Flask(__name__)

# Register routes
configure_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
