#!/bin/bash
set -e

echo "=== BULLETPROOF STARTUP SCRIPT v1.0 ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Files: $(ls -la)"

# Force installation of dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install uvicorn gunicorn fastapi

# Log installed packages
echo "Installed packages:"
pip list | grep -E "uvicorn|fastapi|gunicorn|pydantic"

# Start with simple gunicorn configuration (no worker class)
echo "Starting application with basic gunicorn..."
gunicorn app.main:app --bind=0.0.0.0:8000