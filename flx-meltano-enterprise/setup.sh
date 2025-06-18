#!/bin/bash

# FLX-Meltano Enterprise Setup Script

set -e

echo "🚀 FLX-Meltano Enterprise Setup"
echo "================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.13"

if [[ ! "$python_version" == "$required_version"* ]]; then
    echo "❌ Error: Python $required_version or higher is required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version"

# Check if Poetry is installed
echo "Checking Poetry installation..."
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Installing..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi
echo "✅ Poetry is installed"

# Create virtual environment with Python 3.13
echo "Creating virtual environment..."
poetry env use python3.13

# Install dependencies
echo "Installing dependencies..."
poetry install --no-interaction --verbose

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs data tmp media staticfiles
mkdir -p src/flx/grpc/proto
mkdir -p meltano_projects

# Generate protobuf files
echo "Generating protobuf files..."
poetry run python -m grpc_tools.protoc \
    -I./src/flx/grpc/proto \
    --python_out=./src/flx/grpc/proto \
    --grpc_python_out=./src/flx/grpc/proto \
    ./src/flx/grpc/proto/flx.proto || echo "⚠️  Protobuf generation skipped (proto file may be missing)"

# Setup database
echo "Setting up database..."
if command -v docker &> /dev/null; then
    echo "Starting PostgreSQL and Redis with Docker..."
    docker run -d --name flx-postgres \
        -e POSTGRES_USER=flx \
        -e POSTGRES_PASSWORD=flx_secret \
        -e POSTGRES_DB=flx \
        -p 5432:5432 \
        postgres:16-alpine || echo "⚠️  PostgreSQL container may already exist"

    docker run -d --name flx-redis \
        -p 6379:6379 \
        redis:7-alpine || echo "⚠️  Redis container may already exist"

    echo "Waiting for database to be ready..."
    sleep 5
fi

# Run Django migrations
echo "Running Django migrations..."
cd src && poetry run python -m flx_web.manage makemigrations || echo "⚠️  Migrations skipped"
cd src && poetry run python -m flx_web.manage migrate || echo "⚠️  Migrations skipped"
cd ..

# Create Django superuser
echo "Creating Django superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@flx.local', 'admin123') if not User.objects.filter(username='admin').exists() else None" | cd src && poetry run python -m flx_web.manage shell || echo "⚠️  Superuser creation skipped"
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Run 'make daemon' to start the core daemon"
echo "3. Run 'make web' to start the Django web interface"
echo "4. Run 'make api' to start the FastAPI"
echo "5. Access Django admin at http://localhost:8000/admin (admin/admin123)"
echo ""
echo "For development, run each service in a separate terminal:"
echo "  make daemon    # Core daemon on port 50051"
echo "  make web       # Django on port 8000"
echo "  make api       # FastAPI on port 8001"
echo ""
