@echo off
:: This script ensures the correct modules are installed and starts the app

echo Setting up Python environment...
pip install -r requirements.txt

echo Starting app...
gunicorn main:application --bind=0.0.0.0:8000