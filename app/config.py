import os
import secrets


class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size

    # Model configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "canstralian/WhiteRabbitNeo")

    # CORS settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

    def __init__(self):
        # In production, SECRET_KEY must be set via environment variable
        if not os.getenv("SECRET_KEY"):
            import warnings
            warnings.warn(
                "SECRET_KEY environment variable not set in production. "
                "This is insecure. Please set a strong SECRET_KEY.",
                UserWarning
            )


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
