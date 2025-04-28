import uvicorn
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Print environment info
        logger.info(f"Starting DreamApp Auth API")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Python path: {os.getenv('PYTHONPATH', 'Not set')}")
        
        # Check if we're in Azure
        is_azure = os.getenv("WEBSITE_SITE_NAME") is not None
        if is_azure:
            logger.info("Running in Azure environment")
        else:
            logger.info("Running in local environment")
        
        # Get port from environment variable if running in Azure
        port = int(os.getenv("PORT", os.getenv("WEBSITES_PORT", 8000)))
        logger.info(f"Starting server on port {port}")
        
        # Start the app
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise