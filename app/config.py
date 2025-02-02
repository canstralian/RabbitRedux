import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", True)
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")