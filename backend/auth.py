"""
Authentication System

This module handles user authentication using JWT tokens.
It's designed to be simple and beginner-friendly.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from backend.mysql_db import db

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Security scheme for FastAPI
security = HTTPBearer()


def create_access_token(user_data: Dict[str, Any]) -> str:
    """
    Create a JWT access token for a user
    
    Args:
        user_data: Dictionary containing user information
        
    Returns:
        JWT token string
    """
    # Create token payload
    to_encode = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "full_name": user_data["full_name"],
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }
    
    # Create and return JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token and return user data
    
    Args:
        token: JWT token string
        
    Returns:
        User data dictionary if token is valid, None otherwise
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        # Return user data from token
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "full_name": payload.get("full_name")
        }
        
    except jwt.PyJWTError:
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current user from JWT token
    
    This function is used as a dependency in FastAPI routes that require authentication.
    
    Args:
        credentials: HTTP Authorization credentials from request header
        
    Returns:
        Current user data dictionary
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Verify token
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user still exists in database
    user = db.get_user_by_email(user_data["email"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data


def register_user(full_name: str, email: str, password: str) -> Dict[str, Any]:
    """
    Register a new user
    
    Args:
        full_name: User's full name
        email: User's email address
        password: User's password
        
    Returns:
        Dictionary with success status and user info
        
    Raises:
        HTTPException: If user already exists or validation fails
    """
    try:
        # Basic validation
        if not full_name or not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name, email, and password are required"
            )
        
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Create user in database
        user = db.create_user(full_name, email, password)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": user
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def login_user(email: str, password: str) -> Dict[str, Any]:
    """
    Login a user and return access token
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        Dictionary with access token and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Verify user credentials
    user = db.verify_user_password(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }