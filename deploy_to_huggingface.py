"""
Script to deploy trained models to HuggingFace Hub.
Handles model upload, README generation, and metadata configuration.
"""

import os
import argparse
import logging
from pathlib import Path
from typing import Optional
from huggingface_hub import HfApi, create_repo, upload_folder
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_model_card(
    model_name: str,
    base_model: str,
    accuracy: Optional[float] = None,
    f1_score: Optional[float] = None,
    description: Optional[str] = None
) -> str:
    """
    Create a model card (README.md) for the HuggingFace model.

    Args:
        model_name: Name of the model
        base_model: Base model used for fine-tuning
        accuracy: Model accuracy if available
        f1_score: Model F1 score if available
        description: Optional model description

    Returns:
        Model card content as string
    """
    # TODO: Add automated model card generation using model-card-toolkit
    # TODO: Include training hyperparameters and dataset statistics
    # TODO: Add ethical considerations and bias analysis sections
    metrics_section = ""
    if accuracy or f1_score:
        metrics_section = "## Performance Metrics\n\n"
        if accuracy:
            metrics_section += f"- Accuracy: {accuracy:.2%}\n"
        if f1_score:
            metrics_section += f"- F1 Score: {f1_score:.4f}\n"

    model_card = f"""---
language: en
license: apache-2.0
tags:
- code-classification
- cybersecurity
- transformers
- pytorch
base_model: {base_model}
datasets:
- WhiteRabbitNeo/Code-Functions-Level-Cyber
- WhiteRabbitNeo/WRN-Chapter-1
- WhiteRabbitNeo/WRN-Chapter-2
---

# {model_name}

{description or 'A transformer-based model for code classification with a focus on cybersecurity applications.'}

## Model Description

This model is fine-tuned from `{base_model}` for the task of classifying code snippets, particularly in cybersecurity contexts. It's part of the RabbitRedux project.

{metrics_section}

## Usage

```python
from transformers import pipeline

# Load the model
classifier = pipeline("text-classification", model="{model_name}")

# Classify code
code_snippet = '''
def execute_command(cmd):
    import subprocess
    subprocess.run(cmd, shell=True)
'''

result = classifier(code_snippet)
print(result)
```

## Training

This model was trained using the RabbitRedux training pipeline with:
- Mixed precision training (FP16)
- Data augmentation for code
- Model pruning for efficiency
- Multi-dataset concatenation

## Datasets

The model was trained on cybersecurity-focused code datasets:
- WhiteRabbitNeo/Code-Functions-Level-Cyber
- WhiteRabbitNeo/WRN-Chapter-1
- WhiteRabbitNeo/WRN-Chapter-2
- Additional proprietary datasets

## Limitations

- Maximum sequence length: 512 tokens
- Focused on Python and JavaScript code
- Best performance on security-related code patterns

## Citation

```bibtex
@misc{{rabbitredux2024,
  author = {{Stephen de Jager}},
  title = {{RabbitRedux: Code Classification for Cybersecurity}},
  year = {{2024}},
  publisher = {{GitHub}},
  journal = {{GitHub repository}},
  howpublished = {{\\url{{https://github.com/canstralian/RabbitRedux}}}}
}}
```

## License

Apache 2.0

## Author

**Stephen de Jager (canstralian)**

- GitHub: [@canstralian](https://github.com/canstralian)
- HuggingFace: [@canstralian](https://huggingface.co/canstralian)
"""

    return model_card


def deploy_model(
    model_path: str,
    repo_id: str,
    token: str,
    commit_message: str = "Upload trained model",
    private: bool = False,
    accuracy: Optional[float] = None,
    f1_score: Optional[float] = None
):
    """
    Deploy a trained model to HuggingFace Hub.

    Args:
        model_path: Path to the trained model directory
        repo_id: HuggingFace repository ID (e.g., 'canstralian/RabbitRedux')
        token: HuggingFace API token
        commit_message: Commit message for the upload
        private: Whether to make the repository private
        accuracy: Optional model accuracy
        f1_score: Optional model F1 score
    """
    # TODO: Add model validation before deployment (size, format, inference test)
    # TODO: Implement model versioning with tags and releases
    # TODO: Add rollback capability for failed deployments
    # TODO: Include model performance benchmarks in deployment metadata
    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(f"Model path does not exist: {model_path}")

    logger.info(f"Deploying model from {model_path} to {repo_id}")

    # Initialize HuggingFace API
    api = HfApi()

    # Create repository if it doesn't exist
    try:
        logger.info(f"Creating repository: {repo_id}")
        create_repo(
            repo_id=repo_id,
            token=token,
            private=private,
            repo_type="model",
            exist_ok=True
        )
        logger.info("Repository created or already exists")
    except Exception as e:
        logger.warning(f"Repository creation warning: {e}")

    # Generate model card
    base_model = "distilbert-base-uncased"  # Default, should be read from config
    try:
        # Try to read base model from config.json
        config_path = model_path / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                base_model = config.get("_name_or_path", base_model)
    except Exception as e:
        logger.warning(f"Could not read base model from config: {e}")

    model_card = create_model_card(
        model_name=repo_id,
        base_model=base_model,
        accuracy=accuracy,
        f1_score=f1_score,
        description="Fine-tuned transformer model for cybersecurity-focused code classification"
    )

    # Write model card to model directory
    readme_path = model_path / "README.md"
    with open(readme_path, "w") as f:
        f.write(model_card)
    logger.info(f"Model card written to {readme_path}")

    # Upload folder to HuggingFace
    logger.info("Uploading model to HuggingFace Hub...")
    try:
        api.upload_folder(
            folder_path=str(model_path),
            repo_id=repo_id,
            repo_type="model",
            token=token,
            commit_message=commit_message,
            ignore_patterns=["*.pyc", "__pycache__", ".git", ".gitignore"]
        )
        logger.info(f"✅ Model successfully deployed to https://huggingface.co/{repo_id}")
    except Exception as e:
        logger.error(f"❌ Failed to upload model: {e}")
        raise


def main():
    """Main entry point for the deployment script."""
    parser = argparse.ArgumentParser(description="Deploy trained models to HuggingFace Hub")

    parser.add_argument(
        "--model-path",
        type=str,
        required=True,
        help="Path to the trained model directory"
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        required=True,
        help="HuggingFace repository ID (e.g., 'canstralian/RabbitRedux')"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="HuggingFace API token (or use HF_TOKEN environment variable)"
    )
    parser.add_argument(
        "--commit-message",
        type=str,
        default="Upload trained model",
        help="Commit message for the upload"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Make the repository private"
    )
    parser.add_argument(
        "--accuracy",
        type=float,
        default=None,
        help="Model accuracy (for model card)"
    )
    parser.add_argument(
        "--f1-score",
        type=float,
        default=None,
        help="Model F1 score (for model card)"
    )

    args = parser.parse_args()

    # Get token from args or environment
    token = args.token or os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HuggingFace token required. Provide --token or set HF_TOKEN environment variable")

    # Deploy model
    deploy_model(
        model_path=args.model_path,
        repo_id=args.repo_id,
        token=token,
        commit_message=args.commit_message,
        private=args.private,
        accuracy=args.accuracy,
        f1_score=args.f1_score
    )


if __name__ == "__main__":
    main()
