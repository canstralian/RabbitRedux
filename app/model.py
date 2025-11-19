"""Model loading and classification functions."""

# Load the classifier (this will be loaded once when the module is imported)
classifier = None
try:
    from transformers import pipeline
    classifier = pipeline("text-classification", model="canstralian/WhiteRabbitNeo")
except (ImportError, Exception):
    # For testing purposes, use None if transformers is not available or model fails to load
    classifier = None
