"""
Configuration file for gunicorn server.
Used by Azure App Service to start the application.
"""

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Number of worker processes - reduce for less memory usage
workers = 2

# Maximum number of simultaneous clients
backlog = 2048

# Maximum number of requests a worker will process before restarting
max_requests = 1000

# Restart workers randomly to avoid memory issues
max_requests_jitter = 50

# Timeout for requests
timeout = 30  # Reduced timeout to prevent worker blocking

# Worker timeout for graceful reload
graceful_timeout = 30

# Process name
proc_name = "dreamapp_auth_api"

# Log level
loglevel = "info"

# Use the Uvicorn worker
worker_class = "uvicorn.workers.UvicornWorker"