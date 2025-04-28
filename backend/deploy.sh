#!/bin/bash
set -e

echo "Deploying to Azure App Service..."
echo "Note: Make sure you've configured the following in Azure Portal:"
echo "  - Startup Command: gunicorn --bind=0.0.0.0:8000 app.main:app"
echo "  - Python version: 3.10"

# First run build script
bash build.sh

# Deploy to Azure
echo "Ready for deployment! Deploy using VS Code Azure extension or az webapp deploy command."