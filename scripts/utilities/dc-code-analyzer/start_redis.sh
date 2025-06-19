#!/bin/bash

# Start Redis Server for Code Analyzer
echo "Starting Redis Server..."

# Check if Redis is already running
if pgrep -x "redis-server" >/dev/null; then
	echo "Redis is already running"
	exit 0
fi

# Try to start Redis with different methods
if command -v redis-server &>/dev/null; then
	echo "Starting Redis server..."
	redis-server --daemonize yes --port 6379
	echo "Redis server started on port 6379"
elif command -v docker &>/dev/null; then
	echo "Starting Redis with Docker..."
	docker run -d --name redis-code-analyzer -p 6379:6379 redis:alpine
	echo "Redis container started"
else
	echo "Error: Redis not found. Please install Redis or Docker."
	echo "Ubuntu/Debian: sudo apt-get install redis-server"
	echo "CentOS/RHEL: sudo yum install redis"
	echo "macOS: brew install redis"
	exit 1
fi

# Wait a moment for Redis to start
sleep 2

# Test Redis connection
if redis-cli ping >/dev/null 2>&1; then
	echo "✓ Redis is running and responding to ping"
else
	echo "✗ Redis failed to start or is not responding"
	exit 1
fi
