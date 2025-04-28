from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
import secrets
import string
from dotenv import load_dotenv
from typing import Optional, Tuple, Dict, Any

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
EMAIL_VERIFICATION_EXPIRE_HOURS = 24
PASSWORD_RESET_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_verification_token(data: dict) -> Tuple[str, datetime]:
    """Create an email verification token and its expiry datetime."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=EMAIL_VERIFICATION_EXPIRE_HOURS)
    to_encode.update({"exp": expire, "type": "email_verification"})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire

def create_password_reset_token(data: dict) -> Tuple[str, datetime]:
    """Create a password reset token and its expiry datetime."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "password_reset"})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire

def verify_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify a JWT token and optionally check its type.
    
    Returns the token payload if valid, otherwise raises an exception.
    """
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type if specified
        if expected_type and payload.get("type") != expected_type:
            raise JWTError(f"Token type mismatch, expected {expected_type}")
        
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

def generate_random_string(length: int = 32) -> str:
    """Generate a cryptographically secure random string."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))