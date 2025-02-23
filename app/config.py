import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", True)
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")