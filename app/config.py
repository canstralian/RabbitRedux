import os

def str_to_bool(value):
    """Convert string to boolean."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return value.lower() in ('true', '1', 'yes', 'on')

class Config:
    DEBUG = str_to_bool(os.getenv("FLASK_DEBUG", "False"))
    TESTING = str_to_bool(os.getenv("TESTING", "False"))
    
    # SECRET_KEY must be set in production, but allow a default for testing
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        if TESTING or os.getenv("FLASK_ENV") == "testing":
            SECRET_KEY = "test-secret-key-insecure"
        else:
            raise RuntimeError("SECRET_KEY environment variable must be set and non-empty")