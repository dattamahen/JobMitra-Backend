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
    UserProfileUpdateRequest, PasswordChangeRequest, UserProfileResponse
)
from auth_db import (
    create_user, authenticate_user, get_user_by_id, 
    update_user_profile, change_user_password, seed_users_data, list_all_users
)
from auth_utils import create_access_token, verify_token, SECRET_KEY
from activity_tracker import log_user_activity

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
    """Register a new user with comprehensive profile"""
    try:
        user_data = {
            "email": request.email,
            "password": request.password,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "date_of_birth": request.date_of_birth,
            "phone": request.phone,
            "user_type": request.user_type or "candidate",
            "overall_experience_years": request.overall_experience_years,
            "highest_qualification": request.highest_qualification,
            "skills": request.skills or [],
            "job_preferences": request.job_preferences or [],
            "employment_type": request.employment_type or [],
            # Legacy compatibility
            "username": request.username,
            "city": request.city,
            "state": request.state
        }
        
        user = await create_user(user_data)
        
        # Create response
        return UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            date_of_birth=user.get("date_of_birth"),
            phone=user.get("phone"),
            overall_experience_years=user.get("overall_experience_years"),
            highest_qualification=user.get("highest_qualification"),
            skills=user.get("skills", []),
            user_type=user.get("user_type", "candidate"),
            user_status=user.get("user_status", "active"),
            user_plan=user.get("user_plan", "free"),
            job_preferences=user.get("job_preferences", []),
            employment_type=user.get("employment_type", []),
            profile_created_on=user["profile_created_on"],
            last_active=user["last_active"],
            match_analysis_count=user.get("match_analysis_count", 0),
            match_tailored_count=user.get("match_tailored_count", 0),
            mock_interview_count=user.get("mock_interview_count", 0),
            profile_completion_count=user.get("profile_completion_count", 0),
            profile_visits=user.get("profile_visits", 0),
            # Legacy compatibility
            username=user.get("username"),
            full_name=f"{user['first_name']} {user['last_name']}",
            company_name=user.get("company_name"),
            is_active=user.get("is_active", True),
            is_verified=user.get("is_verified", False),
            profile_completion=user.get("profile_completion_count", 0),
            created_at=user["profile_created_on"].isoformat(),
            city=request.city,
            state=request.state
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
                first_name=user["first_name"],
                last_name=user["last_name"],
                date_of_birth=user.get("date_of_birth"),
                phone=user.get("phone"),
                overall_experience_years=user.get("overall_experience_years"),
                highest_qualification=user.get("highest_qualification"),
                skills=user.get("skills", []),
                user_type=user.get("user_type", "candidate"),
                user_status=user.get("user_status", "active"),
                user_plan=user.get("user_plan", "free"),
                job_preferences=user.get("job_preferences", []),
                employment_type=user.get("employment_type", []),
                profile_created_on=user["profile_created_on"],
                last_active=user["last_active"],
                match_analysis_count=user.get("match_analysis_count", 0),
                match_tailored_count=user.get("match_tailored_count", 0),
                mock_interview_count=user.get("mock_interview_count", 0),
                profile_completion_count=user.get("profile_completion_count", 0),
                profile_visits=user.get("profile_visits", 0),
                # Legacy compatibility
                username=user.get("username"),
                full_name=f"{user['first_name']} {user['last_name']}",
                company_name=user.get("company_name"),
                is_active=user.get("is_active", True),
                is_verified=user.get("is_verified", False),
                profile_completion=user.get("profile_completion_count", 0),
                created_at=user["profile_created_on"].isoformat()
            )
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@auth_router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        print(f"🔍 /auth/me endpoint called for user: {current_user.get('user_id')}")
        print(f"📝 Current user data keys: {list(current_user.keys())}")
        
        return UserProfileResponse(
            user_id=current_user["user_id"],
            email=current_user["email"],
            first_name=current_user["first_name"],
            last_name=current_user["last_name"],
            date_of_birth=current_user.get("date_of_birth"),
            phone=current_user.get("phone"),
            overall_experience_years=current_user.get("overall_experience_years"),
            highest_qualification=current_user.get("highest_qualification"),
            previous_organizations=current_user.get("previous_organizations", []),
            skills=current_user.get("skills", []),
            certifications=current_user.get("certifications", []),
            contributions=current_user.get("contributions"),
            communication_skills=current_user.get("communication_skills", []),
            ai_tools=current_user.get("ai_tools", []),
            social_links=current_user.get("social_links"),
            overall_jobs_applied=current_user.get("overall_jobs_applied", []),
            user_type=current_user.get("user_type", "candidate"),
            user_status=current_user.get("user_status", "active"),
            user_plan=current_user.get("user_plan", "free"),
            job_preferences=current_user.get("job_preferences", []),
            employment_type=current_user.get("employment_type", []),
            profile_created_on=current_user["profile_created_on"],
            last_active=current_user["last_active"],
            match_analysis_count=current_user.get("match_analysis_count", 0),
            match_tailored_count=current_user.get("match_tailored_count", 0),
            mock_interview_count=current_user.get("mock_interview_count", 0),
            profile_completion_count=current_user.get("profile_completion_count", 0),
            profile_visits=current_user.get("profile_visits", 0),
            recent_activity=current_user.get("recent_activity", []),
            # Legacy compatibility
            username=current_user.get("username"),
            full_name=f"{current_user['first_name']} {current_user['last_name']}",
            company_name=current_user.get("company_name"),
            personal_info=current_user.get("personal_info", {}),
            professional_info=current_user.get("professional_info", {}),
            preferences=current_user.get("preferences", {}),
            is_active=current_user.get("is_active", True),
            is_verified=current_user.get("is_verified", False),
            profile_completion=current_user.get("profile_completion_count", 0),
            created_at=current_user["profile_created_on"].isoformat() if hasattr(current_user["profile_created_on"], 'isoformat') else str(current_user["profile_created_on"]),
            updated_at=(current_user.get("updated_at", current_user["profile_created_on"]).isoformat() if hasattr(current_user.get("updated_at", current_user["profile_created_on"]), 'isoformat') else str(current_user.get("updated_at", current_user["profile_created_on"]))),
            last_login=current_user.get("last_login")
        )
    except Exception as e:
        print(f"❌ Error in /auth/me endpoint: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@auth_router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: UserProfileUpdateRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Update user profile with comprehensive fields"""
    try:
        print(f"🔄 Profile update request received for user: {current_user.get('user_id')}")
        print(f"📝 Request data: {request.dict()}")
        
        update_data = {}
        
        # Basic Personal Information
        if request.first_name:
            update_data["first_name"] = request.first_name
        if request.last_name:
            update_data["last_name"] = request.last_name
        if request.date_of_birth:
            update_data["date_of_birth"] = request.date_of_birth
        if request.phone:
            update_data["phone"] = request.phone
            
        # Professional Information
        if request.overall_experience_years is not None:
            update_data["overall_experience_years"] = request.overall_experience_years
        if request.highest_qualification:
            update_data["highest_qualification"] = request.highest_qualification
        if request.previous_organizations:
            update_data["previous_organizations"] = [org.dict() for org in request.previous_organizations]
        if request.skills:
            update_data["skills"] = request.skills
        if request.certifications:
            # Pydantic validator has already processed certifications
            update_data["certifications"] = [cert.dict() if hasattr(cert, 'dict') else cert for cert in request.certifications]
        if request.contributions:
            update_data["contributions"] = request.contributions
        if request.communication_skills:
            update_data["communication_skills"] = [skill.dict() for skill in request.communication_skills]
        if request.ai_tools:
            update_data["ai_tools"] = request.ai_tools
            
        # Social Links - handle both new schema and legacy URL fields
        social_links_update = {}
        
        # New schema social links
        if request.github_link:
            social_links_update["github"] = request.github_link
        if request.youtube_link:
            social_links_update["youtube"] = request.youtube_link
        if request.linkedin_link:
            social_links_update["linkedin"] = request.linkedin_link
        if request.playstore_link:
            social_links_update["playstore"] = request.playstore_link
            
        # Legacy URL fields mapping
        if request.github_url:
            social_links_update["github"] = request.github_url
        if request.youtube_url:
            social_links_update["youtube"] = request.youtube_url
        if request.linkedin_url:
            social_links_update["linkedin"] = request.linkedin_url
        if request.portfolio_url:
            social_links_update["portfolio"] = request.portfolio_url
        if request.twitter_url:
            social_links_update["twitter"] = request.twitter_url
            
        if social_links_update:
            update_data["social_links"] = social_links_update
            
        # User Classification
        if request.user_status:
            update_data["user_status"] = request.user_status
        if request.user_plan:
            update_data["user_plan"] = request.user_plan
            
        # Preferences
        if request.job_preferences:
            update_data["job_preferences"] = request.job_preferences
        if request.employment_type:
            update_data["employment_type"] = request.employment_type
            
        # Legacy compatibility fields
        if request.city or request.state:
            personal_info = current_user.get("personal_info", {})
            location = personal_info.get("location", {})
            if request.city:
                location["city"] = request.city
            if request.state:
                location["state"] = request.state
            personal_info["location"] = location
            update_data["personal_info"] = personal_info
            
        # Legacy professional info mapping
        if any([request.current_role, request.current_company, request.total_experience, 
                request.industry, request.current_salary, request.expected_salary,
                request.desired_job_title, request.professional_summary, 
                request.area_of_expertise, request.key_contributions]):
            professional_info = current_user.get("professional_info", {})
            if request.current_role:
                professional_info["current_role"] = request.current_role
            if request.current_company:
                professional_info["current_company"] = request.current_company
            if request.total_experience:
                professional_info["total_experience"] = request.total_experience
            if request.industry:
                professional_info["industry"] = request.industry
            if request.current_salary is not None:
                professional_info["current_salary"] = request.current_salary
            if request.expected_salary is not None:
                professional_info["expected_salary"] = request.expected_salary
            if request.desired_job_title:
                professional_info["desired_job_title"] = request.desired_job_title
            if request.professional_summary:
                professional_info["professional_summary"] = request.professional_summary
            if request.area_of_expertise:
                professional_info["area_of_expertise"] = request.area_of_expertise
            if request.key_contributions:
                professional_info["key_contributions"] = request.key_contributions
            update_data["professional_info"] = professional_info
        
        # Update last_active timestamp
        update_data["last_active"] = datetime.utcnow()
        
        print(f"📤 Final update data being sent to database: {update_data}")
        
        success = await update_user_profile(current_user["user_id"], update_data)
        
        if not success:
            print(f"❌ Profile update failed for user: {current_user.get('user_id')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
        
        # Log activity
        await log_user_activity(
            current_user["user_id"],
            "profile_update",
            "Updated profile information"
        )
        
        print(f"✅ Profile update successful for user: {current_user.get('user_id')}")
        
        # Get updated user
        updated_user = await get_user_by_id(current_user["user_id"])
        
        return UserResponse(
            user_id=updated_user["user_id"],
            email=updated_user["email"],
            first_name=updated_user["first_name"],
            last_name=updated_user["last_name"],
            date_of_birth=updated_user.get("date_of_birth"),
            phone=updated_user.get("phone"),
            overall_experience_years=updated_user.get("overall_experience_years"),
            highest_qualification=updated_user.get("highest_qualification"),
            skills=updated_user.get("skills", []),
            user_type=updated_user.get("user_type", "candidate"),
            user_status=updated_user.get("user_status", "active"),
            user_plan=updated_user.get("user_plan", "free"),
            job_preferences=updated_user.get("job_preferences", []),
            employment_type=updated_user.get("employment_type", []),
            profile_created_on=updated_user["profile_created_on"],
            last_active=updated_user["last_active"],
            match_analysis_count=updated_user.get("match_analysis_count", 0),
            match_tailored_count=updated_user.get("match_tailored_count", 0),
            mock_interview_count=updated_user.get("mock_interview_count", 0),
            profile_completion_count=updated_user.get("profile_completion_count", 0),
            profile_visits=updated_user.get("profile_visits", 0),
            # Legacy compatibility
            username=updated_user.get("username"),
            full_name=f"{updated_user['first_name']} {updated_user['last_name']}",
            company_name=updated_user.get("company_name"),
            is_active=updated_user.get("is_active", True),
            is_verified=updated_user.get("is_verified", False),
            profile_completion=updated_user.get("profile_completion_count", 0),
            created_at=updated_user["profile_created_on"].isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error in profile update: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
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

@auth_router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user - invalidates the current session"""
    try:
        # In a JWT-based system, logout is mainly handled on the frontend
        # by removing the token. Here we can log the logout event or 
        # implement token blacklisting if needed in the future.
        
        return {
            "message": "Logged out successfully",
            "user_id": current_user["user_id"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
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
