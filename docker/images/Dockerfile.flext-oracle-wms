# =============================================================================
# FLEXT Oracle WMS - Enterprise Docker Environment
# =============================================================================
# Docker container for complete Oracle WMS functionality validation
# Includes all dependencies, testing framework, and real Oracle WMS integration

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables for production compatibility
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system dependencies required for Oracle WMS integration
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry for dependency management
RUN pip install poetry==1.8.3

# Copy Docker-specific dependency files (standalone version)
COPY pyproject.docker.toml ./pyproject.toml

# Generate poetry.lock for Docker standalone dependencies
RUN poetry lock --no-update

# Install dependencies (without dev dependencies for production)  
RUN poetry install --no-dev --no-root && rm -rf $POETRY_CACHE_DIR

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY examples/ ./examples/
COPY scripts/ ./scripts/
COPY .env ./
COPY Makefile ./

# Install the package in development mode for testing
RUN poetry install --no-dev

# Create reports directory for test results
RUN mkdir -p /app/reports

# Set up healthcheck for container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD poetry run python -c "from flext_oracle_wms import FlextOracleWmsClient; print('Oracle WMS Client available')" || exit 1

# Default command runs examples and tests
CMD ["sh", "-c", "echo '🚀 FLEXT Oracle WMS Docker Environment' && echo '📋 Running complete functionality validation...' && poetry run python examples/01_basic_usage.py && poetry run python examples/02_configuration.py && echo '🧪 Running pytest with coverage...' && poetry run pytest --cov=src --cov-report=html --cov-report=term-missing -v"]

# Expose port for potential web interface (future enhancement)
EXPOSE 8080

# Labels for container identification
LABEL maintainer="FLEXT Team <team@flext.sh>"
LABEL version="0.9.0"
LABEL description="Enterprise Oracle WMS integration container with complete functionality validation"
LABEL flext.project="flext-oracle-wms"
LABEL flext.environment="production-compatible"
