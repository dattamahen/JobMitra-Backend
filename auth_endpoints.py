"""
Authentication API endpoints for JobMitra
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime
import jwt

from auth_schemas import (
    LoginRequest, LoginResponse, RegisterRequest, UserResponse,
    UserProfileUpdateRequest, PasswordChangeRequest
)
from auth_db import (
    create_user, authenticate_user, get_user_by_id, 
    update_user_profile, change_user_password, seed_users_data, list_all_users
)
from auth_utils import create_access_token, verify_token, SECRET_KEY

# Create router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = await get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@auth_router.post("/register", response_model=UserResponse)
async def register_user(request: RegisterRequest):
    """Register a new user"""
    try:
        user_data = {
            "email": request.email,
            "username": request.username,
            "password": request.password,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "phone": request.phone,
            "city": request.city,
            "state": request.state
        }
        
        user = await create_user(user_data)
        
        # Create response without password
        return UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            username=user["username"],
            first_name=user["personal_info"]["first_name"],
            last_name=user["personal_info"]["last_name"],
            phone=user["personal_info"]["phone"],
            city=user["personal_info"]["location"]["city"],
            state=user["personal_info"]["location"]["state"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@auth_router.post("/login", response_model=LoginResponse)
async def login_user(request: LoginRequest):
    """Login user with email and password"""
    try:
        user = await authenticate_user(request.email, request.password)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        token_data = {
            "user_id": user["user_id"],
            "email": user["email"]
        }
        token = create_access_token(token_data)
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                user_id=user["user_id"],
                email=user["email"],
                username=user["username"],
                first_name=user["personal_info"]["first_name"],
                last_name=user["personal_info"]["last_name"],
                phone=user["personal_info"]["phone"],
                city=user["personal_info"]["location"]["city"],
                state=user["personal_info"]["location"]["state"],
                is_active=user["is_active"],
                created_at=user["created_at"]
            )
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        return UserResponse(
            user_id=current_user["user_id"],
            email=current_user["email"],
            username=current_user["username"],
            first_name=current_user["personal_info"]["first_name"],
            last_name=current_user["personal_info"]["last_name"],
            phone=current_user["personal_info"]["phone"],
            city=current_user["personal_info"]["location"]["city"],
            state=current_user["personal_info"]["location"]["state"],
            is_active=current_user["is_active"],
            created_at=current_user["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@auth_router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: UserProfileUpdateRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        update_data = {}
        
        if request.first_name:
            update_data["personal_info.first_name"] = request.first_name
        if request.last_name:
            update_data["personal_info.last_name"] = request.last_name
        if request.phone:
            update_data["personal_info.phone"] = request.phone
        if request.city:
            update_data["personal_info.location.city"] = request.city
        if request.state:
            update_data["personal_info.location.state"] = request.state
        if request.current_role:
            update_data["professional_info.current_role"] = request.current_role
        if request.current_company:
            update_data["professional_info.current_company"] = request.current_company
        if request.total_experience:
            update_data["professional_info.total_experience"] = request.total_experience
        if request.industry:
            update_data["professional_info.industry"] = request.industry
        if request.skills:
            update_data["professional_info.skills"] = request.skills
        if request.current_salary is not None:
            update_data["professional_info.current_salary"] = request.current_salary
        if request.expected_salary is not None:
            update_data["professional_info.expected_salary"] = request.expected_salary
        
        success = await update_user_profile(current_user["user_id"], update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
        
        # Get updated user
        updated_user = await get_user_by_id(current_user["user_id"])
        
        return UserResponse(
            user_id=updated_user["user_id"],
            email=updated_user["email"],
            username=updated_user["username"],
            first_name=updated_user["personal_info"]["first_name"],
            last_name=updated_user["personal_info"]["last_name"],
            phone=updated_user["personal_info"]["phone"],
            city=updated_user["personal_info"]["location"]["city"],
            state=updated_user["personal_info"]["location"]["state"],
            is_active=updated_user["is_active"],
            created_at=updated_user["created_at"]
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@auth_router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Verify current password
        user = await authenticate_user(current_user["email"], request.current_password)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Change password
        success = await change_user_password(current_user["user_id"], request.new_password)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@auth_router.post("/seed-users")
async def seed_users():
    """Seed database with test users (development only)"""
    try:
        result = await seed_users_data()
        
        if result is None:
            return {"message": "Users already exist or seeding failed"}
        
        return {
            "message": f"Successfully seeded {len(result)} users",
            "user_ids": [str(id) for id in result]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed users: {str(e)}"
        )

@auth_router.get("/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin endpoint)"""
    try:
        users = await list_all_users()
        return {"users": users, "count": len(users)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )
