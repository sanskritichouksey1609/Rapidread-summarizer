from fastapi import APIRouter, HTTPException, Depends, status
from backend.models import UserRegister, UserLogin, LoginResponse, UserResponse, SuccessResponse
from backend.auth import register_user, login_user, get_current_user
from typing import Dict, Any

# Create router for authentication endpoints
router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_new_user(user_data: UserRegister):
    
    try:
        result = register_user(
            full_name=user_data.full_name,
            email=user_data.email,
            password=user_data.password
        )
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login_existing_user(user_credentials: UserLogin):
    
    try:
        result = login_user(
            email=user_credentials.email,
            password=user_credentials.password
        )
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
  
    try:
        return UserResponse(
            id=current_user["user_id"],
            full_name=current_user["full_name"],
            email=current_user["email"],
            created_at="2024-01-01T00:00:00"  # Placeholder - you can get this from database
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.post("/logout", response_model=SuccessResponse)
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    
    return SuccessResponse(
        success=True,
        message="Logged out successfully"
    )


@router.get("/verify-token")
async def verify_user_token(current_user: Dict[str, Any] = Depends(get_current_user)):
   
    return {
        "valid": True,
        "user": {
            "id": current_user["user_id"],
            "full_name": current_user["full_name"],
            "email": current_user["email"]
        }
    }