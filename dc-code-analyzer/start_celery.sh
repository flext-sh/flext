#!/bin/bash

# Start Celery Worker for Code Analyzer
echo "Starting Celery Worker for Code Analyzer..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Set Django settings
export DJANGO_SETTINGS_MODULE=code_analyzer_web.settings

# Start Celery worker
celery -A code_analyzer_web worker --loglevel=info --concurrency=2

echo "Celery worker stopped" 
