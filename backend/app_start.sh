#!/bin/bash
set -e

# This script is used by Azure App Service to start your application

# Directory navigation
cd /home/site/wwwroot

echo "Starting DreamApp Auth API..."
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Ensure required packages are installed
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "ERROR: requirements.txt not found in $(pwd)"
    find /home/site -name "requirements.txt" -type f
    exit 1
fi

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export ENVIRONMENT="production"
export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1

# Start application with optimized settings
echo "Starting application with gunicorn..."
exec gunicorn app.main:app \
  --bind=0.0.0.0:8000 \
  --workers=2 \
  --worker-class=uvicorn.workers.UvicornWorker \
  --timeout=30 \
  --graceful-timeout=20 \
  --keep-alive=2 \
  --max-requests=1000 \
  --max-requests-jitter=50 \
  --log-level=info \
  --access-logfile=- \
  --error-logfile=- \
  --capture-output