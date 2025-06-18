#!/usr/bin/env python3
"""
Simple FastAPI test server.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# Create simple API
app = FastAPI(title="FLX Test API", version="1.0.0")


class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FLX Test API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="FLX Test API is running",
    )


@app.get("/api/test")
async def test_endpoint():
    """Test endpoint."""
    return {
        "data": "This is a test response",
        "timestamp": "2024-01-01T00:00:00Z",
    }


if __name__ == "__main__":
    print("🚀 Starting FLX Test API on http://localhost:8001")
    print("📚 API docs available at http://localhost:8001/docs")
    print("Press CTRL+C to stop")

    uvicorn.run(app, host="0.0.0.0", port=8001)
