"""
WSGI configuration for Azure App Service.
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log environment info
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")

# Add current directory to Python path to find the app module
sys.path.insert(0, os.getcwd())

# Import the app
try:
    from app.main import app
    logger.info("Successfully imported FastAPI app from app.main")
except ImportError as e:
    logger.error(f"Failed to import app.main: {e}")
    raise

# This is required for WSGI servers
application = app