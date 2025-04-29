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
current_dir = os.getcwd()
logger.info(f"Current directory: {current_dir}")
logger.info(f"Directory contents: {os.listdir('.')}")

# Ensure the app module can be found by adding the directory to Python path
sys.path.insert(0, current_dir)

# Also add parent directory if we're in a subdirectory like 'backend'
parent_dir = os.path.dirname(current_dir)
if os.path.basename(current_dir) == 'backend':
    logger.info(f"Adding parent directory to path: {parent_dir}")
    sys.path.insert(0, parent_dir)

# Log the Python path for debugging
logger.info(f"Python path: {sys.path}")

try:
    # Try importing directly
    try:
        from app.main import app
        logger.info("Successfully imported app.main")
    except ImportError:
        # If we're inside the app directory, adjust import
        if os.path.exists('main.py') and os.path.exists('__init__.py'):
            logger.info("Found main.py in current directory, trying direct import")
            from main import app
            logger.info("Successfully imported main.app")
        else:
            raise
except ImportError as e:
    logger.error(f"Error importing app: {e}")
    # Log detailed information for debugging
    logger.error("Detailed directory structure:")
    for root, dirs, files in os.walk('.', topdown=True):
        for d in dirs:
            if d == 'app' or d == '__pycache__':
                logger.info(f"Found directory: {os.path.join(root, d)}")
        for f in files:
            if f.endswith('.py'):
                logger.info(f"Found Python file: {os.path.join(root, f)}")
    raise

# This is required for Azure to find the app
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("application:application", host="0.0.0.0", port=8000)