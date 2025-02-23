from transformers import pipeline

def load_classifier():
    """Load and return the WhiteRabbitNeo model."""
    return pipeline("text-classification", model="canstralian/WhiteRabbitNeo")

def classify_code(classifier, code_snippet):
    """Classify a given code snippet using the provided classifier."""
    return classifier(code_snippet)