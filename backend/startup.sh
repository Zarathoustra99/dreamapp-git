#!/bin/bash
set -e

echo "Startup script running..."
echo "Current directory: $(pwd)"
echo "Files in root directory: $(ls -la)"

# Make sure we're in the right directory
if [ -f "$(pwd)/backend/requirements.txt" ]; then
    echo "Found requirements.txt in backend directory, changing directory"
    cd backend 
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
export PYTHONPATH=$(pwd)

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

# Check if app module is importable
echo "Testing app import..."
python -c "from app.main import app; print('App import successful')" || {
  echo "Failed to import app.main module. Trying alternative imports..."
  # List the directory structure to diagnose the import issue
  find . -type d -name app -o -name "*.py" | sort
  python -c "import sys; print(sys.path)"
}

# Start the application with optimized settings for Azure
echo "Starting application with gunicorn in Azure..."
# Try to use an absolute app import path for better reliability
export APP_MODULE="app.main:app"
echo "Using app module: $APP_MODULE"

gunicorn $APP_MODULE \
  --bind=0.0.0.0:8000 \
  --workers=2 \
  --worker-class=uvicorn.workers.UvicornWorker \
  --timeout=30 \
  --graceful-timeout=20 \
  --keep-alive=2 \
  --max-requests=1000 \
  --max-requests-jitter=50 \
  --log-level=debug \
  --access-logfile=- \
  --error-logfile=- \
  --capture-output