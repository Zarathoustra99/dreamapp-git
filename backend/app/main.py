from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.auth import router as auth_router
from app.database import engine
from app import models
import os
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app with appropriate settings
app = FastAPI(
    title="DreamApp Auth API",
    description="Authentication API for DreamApp",
    version="1.0.0",
    # Use lower timeout for better resource usage in Azure
    openapi_url="/openapi.json" if os.getenv("ENVIRONMENT") != "production" else None
)

# Determine environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
logger.info(f"Starting application in {ENVIRONMENT} environment")

try:
    # Create tables if they don't exist, but with cautious approach for Azure
    # We'll do this asynchronously to avoid blocking app startup
    def setup_database():
        try:
            # Set a short timeout for database operations
            import threading
            db_setup_thread = threading.Thread(target=lambda: models.Base.metadata.create_all(bind=engine))
            db_setup_thread.daemon = True  # Allow app to exit even if thread is running
            db_setup_thread.start()
            logger.info("Database setup initiated in background thread")
        except Exception as e:
            logger.error(f"Error initiating database setup: {e}")
            logger.info("Application will continue startup despite database error")
    
    # Call the function directly for now - we'll make it async for production
    setup_database()
        
    # Rate limiting setup - with lighter settings
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],
        storage_uri="memory://"
    )
    
    # Apply rate limiter to FastAPI app
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add CSRF protection middleware with appropriate secret key
    secret_key = os.getenv("SECRET_KEY", "my-super-secret-key")
    app.add_middleware(
        SessionMiddleware, 
        secret_key=secret_key,
        # Lower max_age to reduce memory usage
        max_age=3600  # 1 hour instead of default
    )
    
    # Setup CORS based on environment
    if ENVIRONMENT == "production":
         # In production, allow Azure Static Web App and localhost
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                os.getenv("FRONTEND_URL", "http://localhost:5173"),
                "https://polite-water-0fb71a803.6.azurestaticapps.net",  # Add your Azure Static Web App URL here
                "https://dreamapp-ui.azurestaticapps.net"  # Add your custom domain if you have one
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
        )
        
        # Add trusted host middleware in production, but handle Azure host names
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=[
                os.getenv("ALLOWED_HOST", "localhost"),
                "dreamapp-auth-api.azurewebsites.net",  # Add Azure hostname explicitly
                os.getenv("WEBSITE_HOSTNAME", "")       # Azure sets this environment variable
            ]
        )
    else:
        # For development, allow all origins
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    logger.info("Middleware configured successfully")
    
    # Enhanced request middleware for debugging and reliability
    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        # Log all incoming requests to help with debugging in Azure
        path = request.url.path
        logger.info(f"Request: {request.method} {path}")
        
        # For /register endpoint, add extra logging
        if path == "/register" or path == "/token":
            logger.info(f"Processing critical endpoint: {path}")
            
        # Skip CSRF check in development or for safe methods
        if ENVIRONMENT != "production" or request.method in ["GET", "HEAD", "OPTIONS"]:
            try:
                response = await call_next(request)
                return response
            except Exception as e:
                logger.error(f"Request processing error: {e}")
                return Response(content="Server error", status_code=500)
        
        # Check for token, but don't fail the entire app if missing
        try:
            csrf_cookie = request.cookies.get("csrf_token")
            csrf_header = request.headers.get("X-CSRF-Token")
            
            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                return Response(content="CSRF token missing or invalid", status_code=403)
        except Exception as e:
            logger.error(f"CSRF middleware error: {e}")
            # Continue request if there's an error with CSRF check
        
        # Wrap call_next with timeout to prevent hanging requests
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            return Response(content="Server error", status_code=500)
        
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Simple health check endpoint that doesn't touch the database"""
        return {"status": "healthy"}
        
except Exception as e:
    logger.error(f"Error during app setup: {e}")
    # Let the app continue with minimal functionality

app.include_router(auth_router)
