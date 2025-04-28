"""
WSGI configuration for Azure App Service.
This is a standard entry point for many hosting platforms.
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log environment info
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")

# Add current directory to Python path to find the app module
sys.path.insert(0, os.getcwd())

# Import the app
try:
    from app.main import app as application
    logger.info("Successfully imported FastAPI app from app.main")
except ImportError as e:
    logger.error(f"Failed to import app.main: {e}")
    # Try to find where the app module might be
    for root, dirs, files in os.walk('.', topdown=True):
        if '__init__.py' in files and 'main.py' in files:
            logger.info(f"Found potential app module at: {root}")
    raise

# This is required for WSGI servers
app = application