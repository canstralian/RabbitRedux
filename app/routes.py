from flask import request, jsonify
from app.model import get_classifier
import logging

# ----- Setup Logging -----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def configure_routes(app):
    """Configure application routes."""

    @app.route('/')
    def home():
        """Root endpoint displaying project information."""
        return jsonify({
            "project": "RabbitRedux - WhiteRabbitNeo Code Classification Model",
            "description": "A Transformer-based model designed for text classification of code snippets.",
            "repository": "https://github.com/canstralian/WhiteRabbitNeo",
            "author": "Stephen de Jager (canstralian)",
            "license": "Apache 2.0",
            "version": "1.0.0"
        })

    @app.route('/health')
    def health():
        """Health check endpoint for monitoring."""
        return jsonify({
            "status": "healthy",
            "service": "RabbitRedux API"
        }), 200

    @app.route('/classify', methods=['POST'])
    def classify_code():
        """API endpoint to classify code snippets."""
        data = request.get_json()

        if not data or "code" not in data:
            logger.error("Missing 'code' field in request")
            return jsonify({"error": "Missing 'code' field in request"}), 400

        code_snippet = data["code"]

        # Validate input length
        if len(code_snippet) > 10000:
            return jsonify({"error": "Code snippet too long (max 10000 characters)"}), 400

        try:
            model = get_classifier()
            result = model(code_snippet)
            return jsonify({"code": code_snippet, "classification": result})
        except Exception as e:
            logger.error(f"Error during classification: {e}")
            return jsonify({"error": "Internal server error"}), 500
