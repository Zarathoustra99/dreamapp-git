#!/bin/bash
set -e

echo "CUSTOM START SCRIPT RUNNING..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Files: $(ls -la)"

# Install the dependencies
pip install -r requirements.txt

# Show installed packages to verify
pip list

# Start the app
gunicorn app.main:app --bind=0.0.0.0:8000