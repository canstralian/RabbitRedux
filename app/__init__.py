from flask import Flask
from app.routes import configure_routes

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    
    # Load configurations (if needed)
    app.config.from_object("app.config")

    # Register routes
    configure_routes(app)

    return app