"""
Configuration management for RabbitRedux using Pydantic Settings.
Handles environment variables, validation, and application settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = Field(default="RabbitRedux", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development/staging/production)")
    debug: bool = Field(default=False, description="Debug mode")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of workers")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    # Security
    secret_key: str = Field(default="insecure-default-key", description="Secret key for JWT")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    # TODO: Implement JWT-based authentication for user sessions
    # TODO: Add support for multiple API keys with different permission levels
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="CORS allowed origins (comma-separated)"
    )

    # Model Configuration
    default_model: str = Field(default="canstralian/WhiteRabbitNeo", description="Default HuggingFace model")
    model_cache_dir: str = Field(default="./model_cache", description="Model cache directory")
    max_model_length: int = Field(default=512, description="Maximum token length")
    enable_gpu: bool = Field(default=True, description="Enable GPU if available")
    # TODO: Add model quantization options (int8, int4) for memory efficiency
    # TODO: Support multiple model backends (ONNX, TensorRT, OpenVINO)

    # HuggingFace Configuration
    hf_token: Optional[str] = Field(default=None, description="HuggingFace API token")
    hf_home: str = Field(default="./huggingface_cache", description="HuggingFace cache directory")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, description="Requests per minute")

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Metrics endpoint port")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json/text)")

    # Redis (Optional)
    redis_enabled: bool = Field(default=False, description="Enable Redis caching")
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    # TODO: Implement Redis Sentinel support for high availability
    # TODO: Add Redis cluster mode for horizontal scaling

    # Database (Optional)
    database_url: str = Field(default="sqlite:///./rabbitredux.db", description="Database URL")
    # TODO: Add database migration support with Alembic
    # TODO: Implement query result caching for frequently accessed data

    # Performance
    max_batch_size: int = Field(default=32, description="Maximum batch size for classification")
    request_timeout: int = Field(default=300, description="Request timeout in seconds")
    worker_timeout: int = Field(default=600, description="Worker timeout in seconds")

    # Feature Flags
    enable_batch_classification: bool = Field(default=True, description="Enable batch classification")
    enable_model_versioning: bool = Field(default=True, description="Enable model versioning")
    enable_authentication: bool = Field(default=False, description="Enable authentication")
    require_api_key: bool = Field(default=False, description="Require API key for all requests")
    # TODO: Add feature flags for A/B testing different model configurations
    # TODO: Implement gradual rollout controls for new features

    @validator("allowed_origins")
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v.lower()

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    def get_cors_origins(self) -> List[str]:
        """Get CORS allowed origins as a list."""
        if isinstance(self.allowed_origins, list):
            return self.allowed_origins
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()

# Set HuggingFace environment variables if configured
if settings.hf_token:
    os.environ["HUGGINGFACE_TOKEN"] = settings.hf_token
if settings.hf_home:
    os.environ["HF_HOME"] = settings.hf_home
