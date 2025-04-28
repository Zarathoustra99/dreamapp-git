"""
Azure App Service entry point file.
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")

# Ensure the app module can be found by adding the directory to Python path
sys.path.insert(0, os.getcwd())

try:
    # Import the FastAPI app
    from app.main import app
    logger.info("Successfully imported app.main")
except ImportError as e:
    logger.error(f"Error importing app.main: {e}")
    # Try to find the app module
    for root, dirs, files in os.walk('.'):
        if '__init__.py' in files and 'main.py' in files:
            logger.info(f"Potential app directory found at {root}")
    raise

# This is required for Azure to find the app
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("application:app", host="0.0.0.0", port=8000)