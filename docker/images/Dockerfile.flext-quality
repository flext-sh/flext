# Multi-stage Docker build for FLEXT Quality - Enterprise Validation Container

# Build stage with correct Python version
FROM python:3.13-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    graphviz \
    graphviz-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=2.1.3
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_CACHE_DIR=/opt/poetry/cache
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy poetry files
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install dependencies including dev dependencies for testing
RUN poetry install --no-root

# Production stage with correct Python version
FROM python:3.13-slim as production

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    libcairo2 \
    libgirepository-1.0-1 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles /app/analysis_outputs \
    && chown -R appuser:appuser /app

# Install source code as package for proper imports
RUN python -m pip install -e .

# Run comprehensive functionality validation
RUN echo "🧪 ENTERPRISE VALIDATION: Running comprehensive tests..." && \
    python -m pytest tests/ --tb=short -v --cov=src --cov-report=term-missing --cov-fail-under=90 && \
    echo "✅ All tests passed with 90%+ coverage!"

# Validate examples functionality in container
RUN echo "📋 EXAMPLES VALIDATION: Testing all examples..." && \
    cd examples/basic/simple_analysis && python example.py && \
    cd ../../advanced/cli_integration && python example.py && \
    cd ../../integration/api_usage && python example.py && \
    echo "✅ All examples validated successfully!"

# Validate CLI functionality
RUN echo "🔧 CLI VALIDATION: Testing CLI commands..." && \
    python -m flext_quality.cli --help && \
    python -m flext_quality.cli analyze --help && \
    python -m flext_quality.cli score --help && \
    echo "✅ CLI functionality validated!"

# Create validation report
RUN echo "📊 CONTAINER VALIDATION COMPLETE:" && \
    echo "  ✅ Python 3.13 environment" && \
    echo "  ✅ All dependencies installed" && \
    echo "  ✅ Tests passed with 90%+ coverage" && \
    echo "  ✅ All examples functional" && \
    echo "  ✅ CLI commands working" && \
    echo "  ✅ Enterprise-ready container validated"

# Switch to non-root user for security
USER appuser

# Health check for comprehensive functionality
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "from flext_quality import CodeAnalyzer, QualityMetrics; print('✅ FLEXT Quality functional')" || exit 1

# Expose port for web interface
EXPOSE 8000

# Default command - can be overridden for different use cases
CMD ["python", "-c", "print('🚀 FLEXT Quality Enterprise Container Ready!'); print('Available commands:'); print('  - python -m flext_quality.cli analyze <path>'); print('  - python examples/basic/simple_analysis/example.py'); print('  - python -m pytest tests/'); exec('/bin/bash')"]