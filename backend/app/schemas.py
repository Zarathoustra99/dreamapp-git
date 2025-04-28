from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
      
    @field_validator('username')
    def username_must_be_valid(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', v):
             raise ValueError('Username must be 3-30 characters and contain only letters, numbers, underscores, or hyphens')
        return v
           
    @field_validator('password')
    def password_must_be_strong(cls, v):
        import re
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v



class UserOut(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: str
    is_email_verified: bool = True  # Default to true since we removed the column

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    
class RefreshToken(BaseModel):
    refresh_token: str

# Verification and Reset schemas
class VerifyEmail(BaseModel):
    token: str

class RequestPasswordReset(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    password: str
    confirm_password: str
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values.data and v != values.data['password']:
            raise ValueError('Passwords do not match')
        return v
