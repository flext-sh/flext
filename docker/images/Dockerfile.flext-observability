# FLEXT Observability - Monitoring & Metrics Docker Image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user
RUN groupadd -r flext && useradd -r -g flext flext

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Install the application
RUN pip install -e .

# Create directories and set permissions
RUN mkdir -p /app/logs /app/metrics \
    && chown -R flext:flext /app

# Switch to non-root user
USER flext

# Expose metrics port
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9090/metrics || exit 1

# Start the observability service
CMD ["python", "-m", "flext_observability.server"]
