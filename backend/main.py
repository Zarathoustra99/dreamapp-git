"""
Main entry point for Azure App Service.
This is a root-level module to help Azure find the application.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log system information
logger.info(f"Starting DreamApp Auth API")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Import the app - try multiple approaches
try:
    logger.info("Attempting to import from app.main")
    from app.main import app
    logger.info("Successfully imported app from app.main")
except ImportError as e:
    logger.error(f"Error importing from app.main: {e}")
    
    try:
        logger.info("Fallback: checking if app directory exists")
        if os.path.isdir('app') and os.path.isfile('app/main.py'):
            logger.info("app/main.py exists, trying alternative import approach")
            sys.path.insert(0, os.path.join(os.getcwd(), 'app'))
            from main import app
            logger.info("Successfully imported app with alternative approach")
        else:
            logger.error("app directory or app/main.py not found")
            raise ImportError("Cannot find app/main.py")
    except ImportError as e2:
        logger.error(f"Failed to import app with alternative approach: {e2}")
        raise

# For WSGI compatibility
application = app

# For direct running
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting uvicorn server on port {port}")
    uvicorn.run("main:application", host="0.0.0.0", port=port)