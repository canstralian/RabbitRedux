"""
RabbitRedux FastAPI Application
Production-ready ML code classification API with authentication, monitoring, and optimization.
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import asyncio
from functools import lru_cache
import time

from config import settings
from app.model import (
    load_classifier,
    classify_code,
    classify_batch,
    get_model_info,
    clear_model_cache,
    ModelConfig
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Pydantic Models
class CodeClassificationRequest(BaseModel):
    """Request model for single code classification."""
    code: str = Field(..., description="Code snippet to classify", min_length=1, max_length=50000)
    model_name: Optional[str] = Field(None, description="Model to use (defaults to configured model)")
    model_version: Optional[str] = Field(None, description="Specific model version/revision")
    return_all_scores: bool = Field(False, description="Return scores for all labels")

    @validator('code')
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError("Code snippet cannot be empty or whitespace only")
        return v


class BatchClassificationRequest(BaseModel):
    """Request model for batch code classification."""
    codes: List[str] = Field(..., description="List of code snippets to classify", min_items=1)
    model_name: Optional[str] = Field(None, description="Model to use (defaults to configured model)")
    model_version: Optional[str] = Field(None, description="Specific model version/revision")
    return_all_scores: bool = Field(False, description="Return scores for all labels")

    @validator('codes')
    def validate_codes(cls, v):
        if len(v) > settings.max_batch_size:
            raise ValueError(f"Batch size cannot exceed {settings.max_batch_size}")
        if not all(code.strip() for code in v):
            raise ValueError("All code snippets must contain non-whitespace content")
        return v


class ClassificationResponse(BaseModel):
    """Response model for classification results."""
    code: str = Field(..., description="Original code snippet")
    label: str = Field(..., description="Predicted label/category")
    score: float = Field(..., description="Confidence score (0-1)")
    all_scores: Optional[List[Dict[str, Any]]] = Field(None, description="All label scores if requested")
    model_name: str = Field(..., description="Model used for classification")
    timestamp: str = Field(..., description="Classification timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")


class BatchClassificationResponse(BaseModel):
    """Response model for batch classification results."""
    results: List[ClassificationResponse] = Field(..., description="Classification results for each code snippet")
    total_processed: int = Field(..., description="Total number of snippets processed")
    total_time_ms: float = Field(..., description="Total processing time in milliseconds")
    avg_time_per_item_ms: float = Field(..., description="Average time per item in milliseconds")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    environment: str = Field(..., description="Current environment")
    timestamp: str = Field(..., description="Current timestamp")


class ModelInfoResponse(BaseModel):
    """Model information response."""
    model_name: str
    cached: bool
    device: str
    max_length: int
    cache_size: int
    gpu_available: bool


# FastAPI App
app = FastAPI(
    title=settings.app_name,
    description="Production-ready ML API for cybersecurity-focused code classification using transformer models",
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production() else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production() else None,
    openapi_url="/openapi.json" if not settings.is_production() else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics
if settings.enable_metrics:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    logger.info("Prometheus metrics enabled at /metrics")

# Rate limiting storage (simple in-memory, use Redis for production)
# TODO: Replace in-memory rate limiting with Redis for distributed deployments
# TODO: Implement sliding window rate limiting for better fairness
rate_limit_storage: Dict[str, List[float]] = {}


# Dependency Functions
async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Verify API key if authentication is enabled."""
    if not settings.require_api_key:
        return "unauthenticated"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header."
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    return api_key


async def check_rate_limit(request: Request, api_key: str = Depends(verify_api_key)):
    """Simple rate limiting implementation."""
    if not settings.rate_limit_enabled:
        return

    client_id = api_key if api_key != "unauthenticated" else request.client.host
    current_time = time.time()

    if client_id not in rate_limit_storage:
        rate_limit_storage[client_id] = []

    # Remove requests older than 1 minute
    rate_limit_storage[client_id] = [
        req_time for req_time in rate_limit_storage[client_id]
        if current_time - req_time < 60
    ]

    # Check if limit exceeded
    if len(rate_limit_storage[client_id]) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_per_minute} requests per minute."
        )

    # Add current request
    rate_limit_storage[client_id].append(current_time)


@lru_cache()
def get_classifier_cached(model_name: str, version: Optional[str] = None):
    """Cached classifier retrieval."""
    # TODO: Add TTL-based cache expiration for model updates
    # TODO: Implement cache warming on startup for frequently used models
    return load_classifier(model_name, version)


# API Endpoints
@app.get("/", response_model=Dict[str, Any], tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "project": "RabbitRedux",
        "description": "WhiteRabbitNeo Code Classification Model - Transformer-based cybersecurity code analysis",
        "version": settings.app_version,
        "environment": settings.environment,
        "repository": "https://github.com/canstralian/RabbitRedux",
        "author": "Stephen de Jager (canstralian)",
        "license": "Apache 2.0",
        "endpoints": {
            "health": "/health",
            "classify": "/classify",
            "batch_classify": "/batch" if settings.enable_batch_classification else "disabled",
            "model_info": "/model/info",
            "metrics": "/metrics" if settings.enable_metrics else "disabled",
            "docs": "/docs" if not settings.is_production() else "disabled"
        },
        "features": {
            "authentication": settings.enable_authentication,
            "batch_processing": settings.enable_batch_classification,
            "model_versioning": settings.enable_model_versioning,
            "rate_limiting": settings.rate_limit_enabled,
            "metrics": settings.enable_metrics
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Try to get model info to verify it's loaded
        model_loaded = True
        try:
            get_classifier_cached(settings.default_model)
        except Exception as e:
            logger.error(f"Model not loaded: {e}")
            model_loaded = False

        return HealthResponse(
            status="healthy" if model_loaded else "degraded",
            version=settings.app_version,
            model_loaded=model_loaded,
            environment=settings.environment,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/classify", response_model=ClassificationResponse, tags=["Classification"])
async def classify(
    request: CodeClassificationRequest,
    _: str = Depends(check_rate_limit)
):
    """
    Classify a single code snippet.

    - **code**: The code snippet to classify (required)
    - **model_name**: Optional model to use (defaults to configured model)
    - **model_version**: Optional model version/revision
    - **return_all_scores**: Return scores for all labels (default: false)
    """
    # TODO: Add request caching for identical code snippets
    # TODO: Implement async model inference for better concurrency
    # TODO: Add confidence threshold filtering for low-confidence results
    start_time = time.time()

    try:
        # Get model
        model_name = request.model_name or settings.default_model
        classifier = get_classifier_cached(model_name, request.model_version)

        # Classify
        result = classify_code(classifier, request.code, request.return_all_scores)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        processing_time = (time.time() - start_time) * 1000

        return ClassificationResponse(
            code=request.code[:200] + "..." if len(request.code) > 200 else request.code,
            label=result["label"],
            score=result["score"],
            all_scores=result.get("all_scores"),
            model_name=model_name,
            timestamp=datetime.utcnow().isoformat(),
            processing_time_ms=round(processing_time, 2)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Classification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.post("/batch", response_model=BatchClassificationResponse, tags=["Classification"])
async def batch_classify_endpoint(
    request: BatchClassificationRequest,
    _: str = Depends(check_rate_limit)
):
    """
    Classify multiple code snippets in batch for better performance.

    - **codes**: List of code snippets to classify (required, max: configured batch size)
    - **model_name**: Optional model to use (defaults to configured model)
    - **model_version**: Optional model version/revision
    - **return_all_scores**: Return scores for all labels (default: false)
    """
    # TODO: Implement dynamic batching based on available GPU memory
    # TODO: Add priority queue for batch processing
    # TODO: Support streaming results for large batches
    if not settings.enable_batch_classification:
        raise HTTPException(status_code=404, detail="Batch classification is disabled")

    start_time = time.time()

    try:
        # Get model
        model_name = request.model_name or settings.default_model
        classifier = get_classifier_cached(model_name, request.model_version)

        # Classify batch
        results = classify_batch(classifier, request.codes, request.return_all_scores)

        total_time = (time.time() - start_time) * 1000

        # Format responses
        classification_responses = []
        for code, result in zip(request.codes, results):
            if "error" in result:
                logger.warning(f"Error in batch item: {result['error']}")
                continue

            classification_responses.append(
                ClassificationResponse(
                    code=code[:200] + "..." if len(code) > 200 else code,
                    label=result["label"],
                    score=result["score"],
                    all_scores=result.get("all_scores"),
                    model_name=model_name,
                    timestamp=datetime.utcnow().isoformat(),
                    processing_time_ms=None  # Not tracked per-item in batch
                )
            )

        return BatchClassificationResponse(
            results=classification_responses,
            total_processed=len(classification_responses),
            total_time_ms=round(total_time, 2),
            avg_time_per_item_ms=round(total_time / len(request.codes), 2)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch classification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch classification failed: {str(e)}")


@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def model_info(model_name: Optional[str] = None):
    """Get information about the loaded model."""
    import torch

    model_name = model_name or settings.default_model
    info = get_model_info(model_name)

    return ModelInfoResponse(
        model_name=info["model_name"],
        cached=info["cached"],
        device=info["device"],
        max_length=info["max_length"],
        cache_size=info["cache_size"],
        gpu_available=torch.cuda.is_available()
    )


@app.post("/model/clear-cache", tags=["Model"])
async def clear_cache(api_key: str = Depends(verify_api_key)):
    """Clear model cache (requires authentication)."""
    try:
        clear_model_cache()
        get_classifier_cached.cache_clear()
        return {"status": "success", "message": "Model cache cleared"}
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # TODO: Add health check registration with orchestrator (K8s, ECS)
    # TODO: Initialize database connection pool if persistence is added
    # TODO: Pre-load multiple model versions for A/B testing
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API Key authentication: {settings.require_api_key}")

    # Pre-load default model
    try:
        logger.info(f"Loading default model: {settings.default_model}")
        load_classifier(settings.default_model)
        logger.info("Default model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load default model: {e}")
        logger.warning("Application started but model not loaded. Classification will fail.")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application")
    clear_model_cache()


# Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for uncaught errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload,
        workers=settings.api_workers if not settings.reload else 1,
        log_level=settings.log_level.lower(),
        timeout_keep_alive=settings.request_timeout
    )
