#!/bin/bash
set -e

echo "=== DreamApp Auth API Startup ==="
echo "Environment: $ENVIRONMENT"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "WARNING: requirements.txt not found in $(pwd)"
    find . -name "requirements.txt" -type f
fi

# Set Python path explicitly to find modules
export PYTHONPATH=$PYTHONPATH:$(pwd)
export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1

# For debugging in Azure
echo "PYTHONPATH: $PYTHONPATH"
echo "sys.path from Python:"
python -c "import sys; print('\n'.join(sys.path))"

# Create __init__.py if it doesn't exist (making directories into packages)
if [ ! -f "__init__.py" ]; then
    echo "Creating root __init__.py"
    touch __init__.py
fi

# Run diagnostics script
if [ -f "find_modules.py" ]; then
    echo "Running module diagnostics"
    python find_modules.py
else
    echo "Diagnostic script not found"
fi

# Check for proper app file
if [ -f "app/main.py" ]; then
    echo "Found app/main.py - using app.main:app"
    APP_MODULE="app.main:app"
elif [ -f "application.py" ]; then
    echo "Found application.py - using application:application"
    APP_MODULE="application:application"
elif [ -f "../app/main.py" ]; then
    echo "Found ../app/main.py - using app.main:app with adjusted path"
    cd ..
    APP_MODULE="app.main:app"
else
    echo "WARNING: Could not find app module files!"
    find . -name "main.py" | grep -v "__pycache__"
    # Default to application.py as a fallback
    APP_MODULE="application:application" 
fi

echo "Current directory before startup: $(pwd)"
echo "Files in current directory: $(ls -la)"
echo "Starting application with gunicorn using module: $APP_MODULE"

# Start application with gunicorn
exec gunicorn \
  --bind=0.0.0.0:8000 \
  --workers=2 \
  --worker-class=uvicorn.workers.UvicornWorker \
  --timeout=30 \
  --graceful-timeout=20 \
  --keep-alive=2 \
  --log-level=debug \
  --access-logfile=- \
  --error-logfile=- \
  --capture-output \
  $APP_MODULE