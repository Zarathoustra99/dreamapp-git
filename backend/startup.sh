#!/bin/bash
set -e

echo "Startup script running..."
echo "Current directory: $(pwd)"
echo "Files in root directory: $(ls -la)"

# Make sure we're in the right directory
if [ -f "$(pwd)/dreamapp-auth/requirements.txt" ]; then
    echo "Found requirements.txt in dreamapp-auth directory, changing directory"
    cd dreamapp-auth
elif [ -f "$(pwd)/requirements.txt" ]; then
    echo "Found requirements.txt in current directory"
else
    echo "Looking for requirements.txt in subdirectories:"
    find . -name "requirements.txt" -type f
    # Check for parent directory
    if [ -f "../requirements.txt" ]; then
        echo "Found requirements.txt in parent directory"
        cd ..
    fi
fi

echo "Current directory after adjustment: $(pwd)"
echo "Files after adjustment: $(ls -la)"

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "ERROR: requirements.txt not found!"
    exit 1
fi

# Set environment variables for production
export ENVIRONMENT="production"
export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1

# Log more details for debugging
echo "Checking database environment variables..."
if [ -z "$SQL_SERVER" ]; then
    echo "WARNING: SQL_SERVER environment variable not set!"
fi
if [ -z "$WEBSITE_HOSTNAME" ]; then
    echo "DEBUG: Not running in Azure Web App environment"
else
    echo "DEBUG: Running in Azure environment on $WEBSITE_HOSTNAME"
fi

# Start the application with optimized settings for Azure
echo "Starting application with gunicorn in Azure..."
gunicorn app.main:app \
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