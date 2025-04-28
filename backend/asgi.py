import os
import sys

  # Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

  # Import the FastAPI app
from app.main import app

  # This is needed for ASGI compatibility
application = app
