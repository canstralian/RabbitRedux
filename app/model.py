"""
Model loading module for RabbitRedux.
Loads and provides the WhiteRabbitNeo classifier.
"""
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

# Initialize classifier as None
_classifier = None


def get_classifier():
    """
    Load and return the WhiteRabbitNeo classifier.
    Uses lazy loading to avoid loading the model at import time.
    """
    global _classifier
    if _classifier is None:
        try:
            logger.info("Loading WhiteRabbitNeo classifier...")
            _classifier = pipeline("text-classification", model="canstralian/WhiteRabbitNeo")
            logger.info("Classifier loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load classifier: {e}")
            raise
    return _classifier


# Create a module-level classifier instance for backwards compatibility
classifier = get_classifier
