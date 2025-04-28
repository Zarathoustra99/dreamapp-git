from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
import uuid
import os
import platform

from .database import Base

# Always use String(36) for UUID on all database types
# This is most compatible across database systems
id_column_type = String(36)

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'dbo'}  # SQL Server uses dbo schema

    id = Column(id_column_type, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Auth fields
    refresh_token = Column(String(512), nullable=True)
    refresh_token_expires_at = Column(DateTime, nullable=True)
    
    # Status fields
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default='user')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # These are not in the actual database table, so we'll handle them in code
    # without mapping them to database columns
    @property
    def is_email_verified(self):
        # For now, we'll assume users are verified
        return True
        
    def set_email_verification(self, token=None, expires_at=None, verified=False):
        # Store email verification info in memory only
        self._email_verification_token = token
        self._email_verification_expires_at = expires_at
        self._is_email_verified = verified
        
    def get_email_verification_token(self):
        return getattr(self, '_email_verification_token', None)
        
    def get_email_verification_expires_at(self):
        return getattr(self, '_email_verification_expires_at', None)
        
    def set_password_reset(self, token=None, expires_at=None):
        # Store password reset info in memory only
        self._password_reset_token = token
        self._password_reset_expires_at = expires_at
        
    def get_password_reset_token(self):
        return getattr(self, '_password_reset_token', None)
        
    def get_password_reset_expires_at(self):
        return getattr(self, '_password_reset_expires_at', None)