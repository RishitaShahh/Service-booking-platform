"""Pydantic schemas for authentication and authorization requests and responses."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserRegister(BaseModel):
    """Schema for user registration request payload."""
    email: EmailStr = Field(..., description="Valid email address for login")
    password: str = Field(..., min_length=6, description="Plain text password (min 6 characters)")
    full_name: str = Field(..., min_length=2, description="User's full name")
    phone: Optional[str] = Field(None, description="Contact phone number")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="Role: customer or provider")


class UserLogin(BaseModel):
    """Schema for user authentication request payload."""
    email: EmailStr = Field(..., description="User login email")
    password: str = Field(..., description="User login password")


class Token(BaseModel):
    """Schema for OAuth2 JWT token response."""
    access_token: str = Field(..., description="JWT bearer access token")
    token_type: str = Field(default="bearer", description="Token type")
    role: str = Field(..., description="Authenticated user role")
    user_id: int = Field(..., description="Authenticated user ID")
    full_name: str = Field(..., description="Authenticated user full name")


class TokenData(BaseModel):
    """Internal schema representing decoded JWT claims."""
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None
