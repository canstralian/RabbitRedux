from flask import Flask
import os
import logging
from app.routes import configure_routes


def create_app(config_name=None):
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    from app.config import config
    app.config.from_object(config.get(config_name, config['default']))

    # Setup logging
    logging.basicConfig(
        level=logging.INFO if not app.config['DEBUG'] else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Register routes
    configure_routes(app)

    return app
