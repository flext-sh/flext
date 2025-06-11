# DC Code Analyzer Makefile

.PHONY: help install install-dev test lint format type-check security clean docker-build docker-run docker-stop migrate serve docs

# Default target
help:
	@echo "DC Code Analyzer - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Development:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install all dependencies including dev"
	@echo "  migrate          Run database migrations"
	@echo "  serve            Start development server"
	@echo "  shell            Start Django shell"
	@echo ""
	@echo "Code Quality:"
	@echo "  test             Run tests"
	@echo "  test-cov         Run tests with coverage"
	@echo "  lint             Run all linting checks"
	@echo "  format           Format code with black and isort"
	@echo "  type-check       Run type checking with mypy"
	@echo "  security         Run security checks"
	@echo "  pre-commit       Run pre-commit hooks"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run with Docker Compose"
	@echo "  docker-stop      Stop Docker Compose"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean            Clean temporary files and caches"
	@echo ""

# Installation
install:
	poetry install --only=main

install-dev:
	poetry install --with dev
	poetry run pre-commit install

# Development
migrate:
	poetry run python manage.py migrate

serve:
	poetry run python manage.py runserver

shell:
	poetry run python manage.py shell

# Testing
test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=analyzer --cov=dashboard --cov-report=html --cov-report=term-missing

test-ci:
	poetry run pytest --cov=analyzer --cov=dashboard --cov-report=xml --cov-report=term-missing --junitxml=test-results.xml

# Code Quality
lint:
	poetry run ruff check .
	poetry run black --check .
	poetry run isort --check-only .

format:
	poetry run black .
	poetry run isort .
	poetry run ruff check --fix .

type-check:
	poetry run mypy analyzer dashboard

security:
	poetry run bandit -r analyzer dashboard
	poetry run safety check

pre-commit:
	poetry run pre-commit run --all-files

# Analysis
complexity:
	poetry run radon cc analyzer dashboard
	poetry run radon mi analyzer dashboard

dead-code:
	poetry run vulture analyzer dashboard

analyze:
	@echo "Running comprehensive code analysis..."
	@mkdir -p reports
	poetry run ruff check --output-format=json . > reports/ruff.json || true
	poetry run bandit -r analyzer dashboard -f json -o reports/bandit.json || true
	poetry run safety check --json --output reports/safety.json || true
	poetry run vulture analyzer dashboard --json > reports/vulture.json || true
	poetry run radon cc analyzer dashboard -j > reports/radon-cc.json || true
	poetry run radon mi analyzer dashboard -j > reports/radon-mi.json || true
	@echo "Analysis complete. Reports saved in reports/ directory."

# Docker
docker-build:
	docker build -t dc-code-analyzer:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database
db-reset:
	poetry run python manage.py flush --noinput
	poetry run python manage.py migrate

db-backup:
	poetry run python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > backup.json

db-restore:
	poetry run python manage.py loaddata backup.json

# Utilities
collectstatic:
	poetry run python manage.py collectstatic --noinput

superuser:
	poetry run python manage.py createsuperuser

check:
	poetry run python manage.py check

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf reports/

# CI/CD helpers
ci-install:
	poetry install --with dev --no-interaction

ci-test:
	$(MAKE) test-ci

ci-lint:
	$(MAKE) lint type-check security

ci-build:
	poetry build

# Documentation
docs-serve:
	poetry run mkdocs serve

docs-build:
	poetry run mkdocs build

docs-deploy:
	poetry run mkdocs gh-deploy

# Release
bump-patch:
	poetry version patch

bump-minor:
	poetry version minor

bump-major:
	poetry version major

release:
	@echo "Current version: $$(poetry version -s)"
	@echo "Building package..."
	poetry build
	@echo "Package built successfully!"
	@echo "To publish: poetry publish"

# Performance
profile:
	poetry run python -m cProfile -o profile.stats manage.py runserver --noreload

benchmark:
	poetry run pytest tests/ -k "not slow" --benchmark-only