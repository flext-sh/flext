#!/bin/bash

# Django Code Analyzer - Server Startup Script
# This script starts the Django development server with autoreload enabled

cd "$(dirname "$0")" || exit

echo "🚀 Starting Django Code Analyzer Server..."
echo "📝 Server will automatically reload when files change"
echo "🌐 Access the application at: http://localhost:8000"
echo "📊 Admin interface at: http://localhost:8000/REDACTED_LDAP_BIND_PASSWORD"
echo "📦 Package discovery at: http://localhost:8000/packages"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Check if virtual environment exists and activate it
if [ -d "../.venv" ]; then
	echo "🔧 Activating virtual environment..."
	source ../.venv/bin/activate
fi

# Install missing dependencies if needed
echo "📦 Checking dependencies..."
pip install -q sarif-om jschema-to-python 2>/dev/null || true

# Run migrations if needed
echo "🗄️  Checking database migrations..."
python manage.py migrate --noinput

# Start the server with autoreload (default behavior)
echo "🎯 Starting server on 0.0.0.0:8000..."
python manage.py runserver 0.0.0.0:8000
