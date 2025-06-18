#!/bin/bash

# Complete setup script for Code Analyzer
echo "🚀 Starting Code Analyzer System..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    nc -z localhost $1 2>/dev/null
}

# Check Python environment
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Check and start Redis
echo "🔧 Setting up Redis..."
if port_in_use 6379; then
    echo "✓ Redis is already running on port 6379"
else
    if command_exists redis-server; then
        echo "  Starting Redis server..."
        redis-server --daemonize yes --port 6379
        sleep 2
        if port_in_use 6379; then
            echo "✓ Redis server started successfully"
        else
            echo "❌ Failed to start Redis server"
            exit 1
        fi
    else
        echo "❌ Redis not found. Please install Redis:"
        echo "   Ubuntu/Debian: sudo apt-get install redis-server"
        echo "   CentOS/RHEL: sudo yum install redis"
        echo "   macOS: brew install redis"
        exit 1
    fi
fi

# Apply migrations
echo "🗄️  Setting up database..."
python manage.py migrate > /dev/null 2>&1
echo "✓ Database migrations applied"

# Populate backends
echo "⚙️  Populating analysis backends..."
python manage.py populate_backends > /dev/null 2>&1
echo "✓ Analysis backends populated"

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput > /dev/null 2>&1
echo "✓ Static files collected"

# Create superuser if needed (optional)
if [ "$1" = "--create-superuser" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser
fi

# Start services
echo "🌟 Starting services..."

# Start Celery worker in background
echo "  Starting Celery worker..."
celery -A code_analyzer_web worker --loglevel=info --concurrency=2 --detach
echo "✓ Celery worker started"

# Start Django development server
echo "  Starting Django server..."
echo ""
echo "🎉 Code Analyzer is ready!"
echo ""
echo "📍 Access the application at: http://localhost:8000"
echo "🔧 Admin interface at: http://localhost:8000/admin/"
echo "📊 API documentation at: http://localhost:8000/api/v1/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver 8000
