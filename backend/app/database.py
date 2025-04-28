from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import platform
from dotenv import load_dotenv
import logging
import time
import urllib.parse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Debug information
logger.info(f"Platform: {platform.system()} {platform.release()}")
logger.info(f"Python: {platform.python_version()}")

# Use Azure SQL Database
try:
    # Log the connection attempt
    logger.info("Attempting to connect to Azure SQL Database")
    
    # Use the connection string from environment variables
    # Priority: CUSTOM_CONN_STR > SQLCONNSTR_DefaultConnection > manually build from parts
    
    if os.getenv("CUSTOM_CONN_STR"):
        connection_string = os.getenv("CUSTOM_CONN_STR")
        logger.info("Using CUSTOM_CONN_STR environment variable")
    elif os.getenv("SQLCONNSTR_DefaultConnection"):
        connection_string = os.getenv("SQLCONNSTR_DefaultConnection")
        logger.info("Using SQLCONNSTR_DefaultConnection environment variable")
    else:
        # Build connection string from parts
        SERVER = os.getenv("SQL_SERVER", "dreamapp-sqlserver-99999.database.windows.net")
        DATABASE = os.getenv("SQL_DATABASE", "dreamapp-auth-db")
        USERNAME = os.getenv("SQL_USER", "sqladmin")
        PASSWORD = os.getenv("SQL_PASSWORD", "")
        
        if not PASSWORD:
            logger.error("SQL_PASSWORD environment variable is not set")
            raise ValueError("SQL_PASSWORD environment variable is required")
            
        # Build the connection string
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        logger.info(f"Built connection string from parts for Server={SERVER}, Database={DATABASE}, User={USERNAME}")
    
    # Create the SQLAlchemy URL
    DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}"
    logger.info("Successfully created SQLAlchemy URL with connection string")
    
except Exception as e:
    logger.error(f"Failed to set up database connection: {e}")
    raise  # Re-raise to prevent the app from starting with a bad database connection

# Create the SQLAlchemy engine with optimized settings for Azure
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=3,              # Limit connections to avoid memory issues
    max_overflow=5,           # Allow fewer overflow connections to reduce memory
    pool_timeout=15,          # Shorter connection timeout
    pool_recycle=900,         # Recycle connections every 15 minutes
    connect_args={
        "timeout": 15,        # Shorter connection timeout in seconds
        "connect_timeout": 10 # Shorter initial connection timeout
    }
)
logger.info("Created SQL Server engine with optimized settings")

# Create session and base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()