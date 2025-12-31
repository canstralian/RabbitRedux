import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", False)
    TESTING = os.getenv("TESTING", False)
    
    # SECRET_KEY must be set in production, but allow a default for testing
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        if TESTING or os.getenv("FLASK_ENV") == "testing":
            SECRET_KEY = "test-secret-key-insecure"
        else:
            raise RuntimeError("SECRET_KEY environment variable must be set and non-empty")