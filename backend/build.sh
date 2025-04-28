#!/bin/bash
set -e

echo "Running custom build script..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"