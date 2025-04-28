from fastapi import APIRouter, Depends, HTTPException, Response, Request, status, BackgroundTasks, Cookie
from slowapi import Limiter
from slowapi.util import get_remote_address
import secrets
import logging

# Set up logging
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from app import schemas, models, utils
from app.database import get_db
from app.email_service import send_verification_email, send_password_reset_email
from jose import JWTError
from typing import Optional
import os

router = APIRouter()

@router.get("/ping")
def ping():
    """Simple endpoint to test if the API is working"""
    logger.info("Ping endpoint called")
    return {"status": "ok", "message": "API is working"}

@router.post("/test-register")
def test_register(user: schemas.UserCreate):
    """Test endpoint for registration that doesn't touch the database"""
    logger.info(f"Test registration received - Email: {user.email}, Username: {user.username}")
    return {
        "id": "test-id-123",
        "email": user.email,
        "username": user.username,
        "role": "user"
    }

@router.post("/register", response_model=schemas.UserOut)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user: schemas.UserCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    logger.info(f"Registration attempt - Email: {user.email}, Username: {user.username}")
    
    try:
        # Add timeout handling for database operations
        import time
        start_time = time.time()
        
        # Check if email already exists - with simplified logic
        user_exists = False
        try:
            existing_email = db.query(models.User).filter(models.User.email == user.email).first()
            if existing_email:
                logger.info(f"Email {user.email} already exists")
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Check if username already exists
            existing_username = db.query(models.User).filter(models.User.username == user.username).first()
            if existing_username:
                logger.info(f"Username {user.username} already exists")
                raise HTTPException(status_code=400, detail="Username already taken")
        except Exception as db_error:
            logger.error(f"Database error during user check: {db_error}")
            raise HTTPException(status_code=500, detail="Error checking user availability")
            
        # Log database query time
        logger.info(f"Database query time: {time.time() - start_time:.2f} seconds")

        # Hash the password
        hashed_pw = utils.hash_password(user.password)
        
        # Generate email verification token
        verification_token, token_expires = utils.create_verification_token({"email": user.email})
        
        # Create new user
        new_user = models.User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_pw
        )
        
        # Set email verification info using our new method
        new_user.set_email_verification(
            token=verification_token,
            expires_at=token_expires
        )
        
        # Add to database
        db_start = time.time()
        logger.info("Adding user to database...")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Database save time: {time.time() - db_start:.2f} seconds")
        
        # Send verification email in the background
        try:
            # Only send email if mail configuration is set
            if os.getenv("MAIL_SERVER") and os.getenv("MAIL_USERNAME"):
                # In Azure, we'll log but skip actual email sending initially to avoid timeouts
                if os.getenv("WEBSITE_SITE_NAME"):
                    logger.info(f"Email would be sent to {user.email} with token {verification_token[:10]}...")
                else:
                    background_tasks.add_task(
                        send_verification_email,
                        user.email,
                        verification_token
                    )
        except Exception as email_error:
            logger.error(f"Failed to send verification email: {str(email_error)}")
            # Don't raise error here, just log it
        
        logger.info(f"User registered successfully: {new_user.id}")
        return new_user
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        # Provide a cleaner error message to avoid exposing internal details
        raise HTTPException(status_code=500, detail="Registration failed due to a server error")

@router.post("/verify-email")
async def verify_email(
    verification_data: schemas.VerifyEmail,
    db: Session = Depends(get_db)
):
    """Verify a user's email using the verification token."""
    try:
        # Verify the token
        payload = utils.verify_token(verification_data.token, "email_verification")
        email = payload.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Invalid verification token")
        
        # Find the user
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if the token matches and is not expired
        token = user.get_email_verification_token()
        expires_at = user.get_email_verification_expires_at()
        
        if (token != verification_data.token or 
            (expires_at and expires_at < datetime.utcnow())):
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        # Mark email as verified and clear the verification token
        user.set_email_verification(verified=True)
        
        # Update the user
        db.commit()
        
        return {"message": "Email verified successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/request-password-reset")
@limiter.limit("3/minute")
async def request_password_reset(
    request: Request,
    reset_request: schemas.RequestPasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request a password reset by email."""
    # Find the user by email
    user = db.query(models.User).filter(models.User.email == reset_request.email).first()
    
    # Always return success to prevent email enumeration attacks
    if not user:
        return {"message": "If a user with that email exists, a password reset link has been sent"}
    
    # Generate a password reset token
    reset_token, token_expires = utils.create_password_reset_token({"sub": str(user.id)})
    
    # Store the token and expiry time using our method
    user.set_password_reset(token=reset_token, expires_at=token_expires)
    db.commit()
    
    # Send the password reset email in the background
    try:
        # Only send email if mail configuration is set
        if os.getenv("MAIL_SERVER") and os.getenv("MAIL_USERNAME"):
            background_tasks.add_task(
                send_password_reset_email,
                user.email,
                reset_token
            )
    except Exception as email_error:
        logger.error(f"Failed to send password reset email: {str(email_error)}")
        # Don't raise error here, just log it
    
    return {"message": "If a user with that email exists, a password reset link has been sent"}

@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    reset_data: schemas.ResetPassword,
    db: Session = Depends(get_db)
):
    """Reset a user's password using a reset token."""
    try:
        # Verify the token
        payload = utils.verify_token(reset_data.token, "password_reset")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid reset token")
        
        # Find the user
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if the token matches and is not expired
        token = user.get_password_reset_token()
        expires_at = user.get_password_reset_expires_at()
        
        if (token != reset_data.token or 
            (expires_at and expires_at < datetime.utcnow())):
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Hash the new password
        hashed_password = utils.hash_password(reset_data.password)
        
        # Update the password and clear the reset token
        user.hashed_password = hashed_password
        user.set_password_reset()
        
        # Update the user
        db.commit()
        
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/token", response_model=schemas.Token)
@limiter.limit("10/minute")
def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Better logging
    logger.info(f"Login attempt - Username/Email: {form_data.username}")
    
    # Check if the input is an email (contains @) or a username
    if "@" in form_data.username:
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
        logger.info(f"Searching by email: {form_data.username}, Found user: {user is not None}")
    else:
        user = db.query(models.User).filter(models.User.username == form_data.username).first()
        logger.info(f"Searching by username: {form_data.username}, Found user: {user is not None}")
        
    if not user:
        logger.info("User not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    password_valid = utils.verify_password(form_data.password, user.hashed_password)
    logger.info(f"Password verification result: {password_valid}")
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Optional: Check if email is verified (comment out if you want to allow login without verification)
    # if not user.is_email_verified:
    #     raise HTTPException(status_code=401, detail="Email not verified")

    access_token = utils.create_access_token({"sub": str(user.id)})
    refresh_token = utils.create_refresh_token({"sub": str(user.id)})

    user.refresh_token = refresh_token
    user.refresh_token_expires_at = datetime.utcnow() + timedelta(days=utils.REFRESH_TOKEN_EXPIRE_DAYS)
    db.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # True in production (Azure requires it)
        samesite="none",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/refresh"
    )

    return schemas.Token(access_token=access_token, refresh_token=None)  

@router.post("/refresh", response_model=schemas.Token)
@limiter.limit("20/minute")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = utils.verify_token(token, "refresh")
        user_id = payload.get("sub")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.refresh_token != token or user.refresh_token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Issue new tokens
    new_access_token = utils.create_access_token({"sub": str(user.id)})
    new_refresh_token = utils.create_refresh_token({"sub": str(user.id)})

    # Save new refresh token
    user.refresh_token = new_refresh_token
    user.refresh_token_expires_at = datetime.utcnow() + timedelta(days=utils.REFRESH_TOKEN_EXPIRE_DAYS)
    db.commit()

    # Set new cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/refresh"
    )

    return schemas.Token(access_token=new_access_token, refresh_token=None)

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token", path="/refresh")
    response.delete_cookie("csrf_token")
    return {"message": "Logged out"}

@router.get("/csrf-token")
def get_csrf_token(response: Response):
    """
    Generate and set a CSRF token as a cookie.
    The frontend should call this endpoint and then use the token in the X-CSRF-Token header for subsequent requests.
    """
    token = secrets.token_hex(32)
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=8 * 60 * 60  # 8 hours
    )
    return {"csrf_token": token}