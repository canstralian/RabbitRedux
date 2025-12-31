"""
Model loading and classification module for RabbitRedux.
Provides utilities for loading transformer models and performing code classification.
"""

from transformers import pipeline
import logging
from functools import lru_cache
from typing import Dict, List, Any, Optional
import torch

logger = logging.getLogger(__name__)

# Global model cache
# TODO: Replace global dict with LRU cache with size limits
# TODO: Add model cache persistence to disk for faster restarts
_model_cache: Dict[str, Any] = {}


class ModelConfig:
    """Configuration for model loading and inference."""

    DEFAULT_MODEL = "canstralian/WhiteRabbitNeo"
    FALLBACK_MODELS = [
        "canstralian/RabbitRedux",
        "distilbert-base-uncased"
    ]
    MAX_LENGTH = 512
    DEVICE = 0 if torch.cuda.is_available() else -1  # GPU if available
    # TODO: Add support for multi-GPU inference with model parallelism
    # TODO: Implement automatic mixed precision (AMP) for faster inference
    # TODO: Add ONNX runtime support for optimized CPU inference


@lru_cache(maxsize=3)
def load_classifier(model_name: str = ModelConfig.DEFAULT_MODEL, version: Optional[str] = None):
    """
    Load and cache a text classification model.

    Args:
        model_name: HuggingFace model identifier
        version: Optional model version/revision

    Returns:
        HuggingFace pipeline for text classification

    Raises:
        Exception: If model loading fails
    """
    # TODO: Add model compilation with torch.compile() for PyTorch 2.0+
    # TODO: Implement model warmup with sample inputs after loading
    # TODO: Add telemetry for model load times and success rates
    cache_key = f"{model_name}:{version or 'latest'}"

    if cache_key in _model_cache:
        logger.info(f"Using cached model: {cache_key}")
        return _model_cache[cache_key]

    try:
        logger.info(f"Loading model: {model_name} (version: {version or 'latest'})")

        pipeline_kwargs = {
            "task": "text-classification",
            "model": model_name,
            "device": ModelConfig.DEVICE,
            "max_length": ModelConfig.MAX_LENGTH,
            "truncation": True
        }

        if version:
            pipeline_kwargs["revision"] = version

        classifier = pipeline(**pipeline_kwargs)
        _model_cache[cache_key] = classifier

        logger.info(f"Model loaded successfully: {cache_key}")
        logger.info(f"Using device: {'GPU' if ModelConfig.DEVICE >= 0 else 'CPU'}")

        return classifier

    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")

        # Try fallback models
        for fallback in ModelConfig.FALLBACK_MODELS:
            if fallback != model_name:
                try:
                    logger.warning(f"Attempting fallback model: {fallback}")
                    return load_classifier(fallback)
                except Exception as fallback_error:
                    logger.error(f"Fallback model {fallback} failed: {fallback_error}")
                    continue

        raise Exception(f"All model loading attempts failed. Last error: {e}")


def classify_code(classifier, code_snippet: str, return_all_scores: bool = False) -> Dict[str, Any]:
    """
    Classify a code snippet using the provided classifier.

    Args:
        classifier: HuggingFace pipeline
        code_snippet: Code to classify
        return_all_scores: If True, return scores for all labels

    Returns:
        Dictionary with classification results
    """
    # TODO: Add preprocessing for code normalization (remove comments, whitespace)
    # TODO: Implement ensemble predictions with multiple models
    # TODO: Add explanation/attribution support using SHAP or LIME
    try:
        result = classifier(
            code_snippet,
            top_k=None if return_all_scores else 1,
            truncation=True,
            max_length=ModelConfig.MAX_LENGTH
        )

        # Handle both single and batch results
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], dict):
                # Single classification result
                return {
                    "label": result[0]["label"],
                    "score": float(result[0]["score"]),
                    "all_scores": result if return_all_scores else None
                }
            elif isinstance(result[0], list):
                # Multiple classifications (shouldn't happen with single input)
                return {
                    "label": result[0][0]["label"],
                    "score": float(result[0][0]["score"]),
                    "all_scores": result[0] if return_all_scores else None
                }

        return {"error": "Unexpected result format", "raw_result": result}

    except Exception as e:
        logger.error(f"Classification error: {e}")
        return {"error": str(e)}


def classify_batch(classifier, code_snippets: List[str], return_all_scores: bool = False) -> List[Dict[str, Any]]:
    """
    Classify multiple code snippets in batch for better performance.

    Args:
        classifier: HuggingFace pipeline
        code_snippets: List of code snippets to classify
        return_all_scores: If True, return scores for all labels

    Returns:
        List of classification results
    """
    # TODO: Implement adaptive batch sizing based on GPU memory usage
    # TODO: Add batch splitting for very large inputs
    # TODO: Support async batch processing with progress callbacks
    try:
        results = classifier(
            code_snippets,
            top_k=None if return_all_scores else 1,
            truncation=True,
            max_length=ModelConfig.MAX_LENGTH,
            batch_size=8  # Adjust based on available memory
        )

        processed_results = []
        for result in results:
            if isinstance(result, list) and len(result) > 0:
                processed_results.append({
                    "label": result[0]["label"],
                    "score": float(result[0]["score"]),
                    "all_scores": result if return_all_scores else None
                })
            else:
                processed_results.append({"error": "Unexpected result format"})

        return processed_results

    except Exception as e:
        logger.error(f"Batch classification error: {e}")
        return [{"error": str(e)} for _ in code_snippets]


def get_model_info(model_name: str = ModelConfig.DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Get information about the loaded model.

    Args:
        model_name: Model identifier

    Returns:
        Dictionary with model metadata
    """
    cache_key = f"{model_name}:latest"

    return {
        "model_name": model_name,
        "cached": cache_key in _model_cache,
        "device": "GPU" if ModelConfig.DEVICE >= 0 else "CPU",
        "max_length": ModelConfig.MAX_LENGTH,
        "cache_size": len(_model_cache)
    }


def clear_model_cache():
    """Clear all cached models to free memory."""
    global _model_cache
    _model_cache.clear()
    load_classifier.cache_clear()
    logger.info("Model cache cleared")


# Initialize default classifier at module import
try:
    classifier = load_classifier()
except Exception as e:
    logger.error(f"Failed to initialize default classifier: {e}")
    classifier = None
