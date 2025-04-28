#!/usr/bin/env python3
"""
Debug script for Azure App Service.
This script can be run directly in Azure to test basic functionality.
Example Kudu console command: python debug_azure.py
"""
import os
import sys
import logging
import importlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("debug_azure")

def main():
    """Main debug function to check Azure environment."""
    logger.info("=== Azure Environment Debug ===")

    # System info
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python path: {sys.executable}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Environment variables
    logger.info("=== Environment Variables ===")
    for key in sorted(os.environ):
        if key.startswith('WEBSITE_') or key.startswith('PYTHON') or key in ('PORT', 'PATH'):
            logger.info(f"{key}: {os.environ[key]}")
    
    # Directory structure
    logger.info("=== Directory Structure ===")
    logger.info(f"Current directory contents: {os.listdir('.')}")
    if os.path.isdir('app'):
        logger.info(f"App directory contents: {os.listdir('app')}")
    
    # Python path
    logger.info("=== Python Path ===")
    for path in sys.path:
        logger.info(f"  - {path}")
    
    # Test imports
    logger.info("=== Module Import Tests ===")
    modules_to_test = [
        'fastapi', 'uvicorn', 'gunicorn',
        'app', 'app.main', 'application'
    ]
    
    for module in modules_to_test:
        try:
            logger.info(f"Trying to import {module}...")
            spec = importlib.util.find_spec(module)
            if spec:
                logger.info(f"  ✓ Module {module} found at: {spec.origin}")
                if module in ('app.main', 'application'):
                    mod = importlib.import_module(module)
                    if hasattr(mod, 'app'):
                        logger.info(f"  ✓ app object found in {module}")
                    else:
                        logger.info(f"  ✗ app object NOT found in {module}")
            else:
                logger.info(f"  ✗ Module {module} not found")
        except ImportError as e:
            logger.info(f"  ✗ Error importing {module}: {e}")
            
    logger.info("Debug complete!")

if __name__ == "__main__":
    main()