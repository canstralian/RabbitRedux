.PHONY: help install install-dev test lint format clean run docker-build docker-run

help:
	@echo "RabbitRedux - Available Commands"
	@echo "================================="
	@echo "install         - Install production dependencies"
	@echo "install-dev     - Install development dependencies"
	@echo "test            - Run test suite"
	@echo "test-cov        - Run tests with coverage"
	@echo "lint            - Run code linting"
	@echo "format          - Format code with black and isort"
	@echo "security        - Run security checks"
	@echo "clean           - Remove cache and build files"
	@echo "run             - Run development server"
	@echo "run-prod        - Run production server with Gunicorn"
	@echo "docker-build    - Build Docker image"
	@echo "docker-run      - Run Docker container"
	@echo "docker-compose  - Run with docker-compose"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app/ tests/ --max-line-length=127
	pylint app/ tests/ || true

format:
	black app/ tests/ --line-length=127
	isort app/ tests/ --profile black --line-length=127

security:
	bandit -r app/ -ll
	safety check

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

run:
	FLASK_ENV=development python app.py

run-prod:
	gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --timeout 120 wsgi:app

docker-build:
	docker build -t rabbitredux:latest .

docker-run:
	docker run -d -p 5000:5000 --name rabbitredux -e SECRET_KEY=$$(python -c 'import secrets; print(secrets.token_hex(32))') rabbitredux:latest

docker-compose:
	docker-compose up -d

docker-stop:
	docker-compose down
	docker stop rabbitredux 2>/dev/null || true
	docker rm rabbitredux 2>/dev/null || true
