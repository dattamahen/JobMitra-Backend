"""
Authentication API endpoints for JobMitra
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime
import logging
import jwt

logger = logging.getLogger(__name__)

from auth_schemas import (
    LoginRequest, LoginResponse, RegisterRequest, UserResponse,
    UserProfileUpdateRequest, PasswordChangeRequest, UserProfileResponse,
    ForgotPasswordRequest, ResetPasswordRequest
)
from auth_db import (
    create_user, authenticate_user, get_user_by_id, get_user_by_email,
    update_user_profile, change_user_password, seed_users_data, list_all_users
)
from db import db
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

        # Check if token has been blacklisted (logged out)
        from token_blacklist import is_token_blacklisted
        if is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

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
            logger.warning("User not found for ID: %s", user_id)
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
        logger.error("Auth error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@auth_router.post("/register", response_model=UserResponse)
async def register_user(request: RegisterRequest):
    """Register a new user with minimal required fields"""
    try:
        user_data = {
            "email": request.email,
            "password": request.password,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "user_type": request.user_type
        }
        
        # HR accounts require company email + email verification
        if request.user_type in ("hire", "hr"):
            from email_domain_validator import is_company_email
            if not is_company_email(request.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="HR registration requires a company email address. Public email providers (Gmail, Yahoo, Outlook, etc.) are not allowed."
                )
            user_data["user_status"] = "pending_verification"
        
        user = await create_user(user_data)
        
        # Send verification email for HR users
        if request.user_type in ("hire", "hr"):
            from email_service import email_service
            from auth_utils import generate_verification_token
            token = generate_verification_token()
            # Store token in DB
            await db.database["users"].update_one(
                {"user_id": user["user_id"]},
                {"$set": {"verification_token": token, "user_status": "pending_verification"}}
            )
            user_name = f"{request.first_name} {request.last_name}"
            email_service.send_verification_email(request.email, token, user_name)
        
        # Create response
        return UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            skills=user.get("skills", []),
            user_type=user.get("user_type", "candidate"),
            user_status=user.get("user_status", "active"),
            user_plan=user.get("user_plan", "free"),
            profile_created_on=user["profile_created_on"],
            last_active=user["last_active"],
            match_analysis_count=user.get("match_analysis_count", 0),
            match_tailored_count=user.get("match_tailored_count", 0),
            mock_interview_count=user.get("mock_interview_count", 0),
            profile_completion_count=user.get("profile_completion_count", 0),
            profile_visits=user.get("profile_visits", 0),
            full_name=f"{user['first_name']} {user['last_name']}",
            is_active=user.get("is_active", True),
            is_verified=user.get("is_verified", False),
            created_at=user["profile_created_on"].isoformat()
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
                feature_usage_count=user.get("feature_usage_count", 5),
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

@auth_router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        return {
            "user_id": current_user["user_id"],
            "email": current_user["email"],
            "first_name": current_user["first_name"],
            "last_name": current_user["last_name"],
            "date_of_birth": current_user.get("date_of_birth"),
            "phone": current_user.get("phone"),
            "skills": current_user.get("skills", []),
            "technical_skills": current_user.get("technical_skills", []),
            "work_experience": current_user.get("work_experience", []),
            "education": current_user.get("education", []),
            "projects": current_user.get("projects", []),
            "certifications": current_user.get("certifications", []),
            "professional_summary": current_user.get("professional_summary"),
            "current_role": current_user.get("current_role"),
            "current_company": current_user.get("current_company"),
            "desired_job_title": current_user.get("desired_job_title"),
            "expected_salary": current_user.get("expected_salary"),
            "currency": current_user.get("currency"),
            "linkedin_link": current_user.get("linkedin_link"),
            "github_link": current_user.get("github_link"),
            "portfolio_link": current_user.get("portfolio_link"),
            "city": current_user.get("city"),
            "state": current_user.get("state"),
            "job_preferences": current_user.get("job_preferences", []),
            "employment_type": current_user.get("employment_type", []),
            "overall_experience_years": current_user.get("overall_experience_years"),
            "highest_qualification": current_user.get("highest_qualification"),
            "feature_usage_count": current_user.get("feature_usage_count", 5),
            "user_plan": current_user.get("user_plan", "free")
        }
    except Exception as e:
        logger.error("Error in /auth/me: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get profile")

@auth_router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: UserProfileUpdateRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Update user profile with comprehensive fields"""
    try:
        logger.debug("Profile update request for user: %s", current_user.get('user_id'))
        
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
        if request.technical_skills:
            update_data["technical_skills"] = request.technical_skills
        if request.work_experience:
            update_data["work_experience"] = request.work_experience
        if request.education:
            update_data["education"] = request.education
        if request.projects:
            update_data["projects"] = request.projects
        if request.certifications:
            # Process certifications as objects
            update_data["certifications"] = request.certifications
        if request.contributions:
            update_data["contributions"] = request.contributions
        if request.communication_skills:
            update_data["communication_skills"] = [skill.dict() for skill in request.communication_skills]
        if request.ai_tools:
            update_data["ai_tools"] = request.ai_tools
        if request.professional_summary:
            update_data["professional_summary"] = request.professional_summary
        if request.current_role:
            update_data["current_role"] = request.current_role
        if request.current_company:
            update_data["current_company"] = request.current_company
        if request.portfolio_link:
            update_data["portfolio_link"] = request.portfolio_link
        if request.desired_job_title:
            update_data["desired_job_title"] = request.desired_job_title
        if request.expected_salary is not None:
            update_data["expected_salary"] = request.expected_salary
        if request.currency:
            update_data["currency"] = request.currency
        if request.linkedin_link:
            update_data["linkedin_link"] = request.linkedin_link
        if request.github_link:
            update_data["github_link"] = request.github_link
        if request.city:
            update_data["city"] = request.city
        if request.state:
            update_data["state"] = request.state
            
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
        
        success = await update_user_profile(current_user["user_id"], update_data)
        
        if not success:
            logger.warning("Profile update failed for user: %s", current_user.get('user_id'))
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
        
        logger.info("Profile updated for user: %s", current_user.get('user_id'))
        
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
            certifications=updated_user.get("certifications", []),
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
            city=updated_user.get("city"),
            state=updated_user.get("state"),
            is_active=updated_user.get("is_active", True),
            is_verified=updated_user.get("is_verified", False),
            profile_completion=updated_user.get("profile_completion_count", 0),
            created_at=updated_user["profile_created_on"].isoformat()
        )
        
    except Exception as e:
        logger.error("Error in profile update: %s", e)
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

@auth_router.post("/logout")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user - blacklists the current token"""
    try:
        from token_blacklist import blacklist_token
        token = credentials.credentials
        blacklist_token(token)

        # Decode to get user_id for logging
        payload = verify_token(token)
        user_id = payload.get("user_id", "unknown") if payload else "unknown"

        return {
            "message": "Logged out successfully",
            "user_id": user_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@auth_router.post("/seed-users")
async def seed_users():
    """Seed database with test users (development only)"""
    if settings.APP_ENV not in ("local", "dev"):
        raise HTTPException(status_code=403, detail="Not available in production")
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

@auth_router.get("/check-schema")
async def check_user_schema():
    """Check current user schema in database"""
    if settings.APP_ENV not in ("local", "dev"):
        raise HTTPException(status_code=403, detail="Not available in production")
    try:
        from db import db
        
        # Get a sample user to see current schema
        sample_user = await db.database["users"].find_one({})
        if sample_user:
            # Remove sensitive data
            sample_user.pop("password_hash", None)
            sample_user.pop("password", None)
            sample_user["_id"] = str(sample_user["_id"])
        
        # Get distinct user_plan values
        user_plans = await db.database["users"].distinct("user_plan")
        
        # Count users
        total_users = await db.database["users"].count_documents({})
        
        return {
            "total_users": total_users,
            "user_plan_values": user_plans,
            "sample_user": sample_user
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema check failed: {str(e)}"
        )

@auth_router.post("/migrate-feature-usage")
async def migrate_feature_usage():
    """Add feature usage count to existing users"""
    if settings.APP_ENV not in ("local", "dev"):
        raise HTTPException(status_code=403, detail="Not available in production")
    try:
        from db import db
        
        # Simply add feature_usage_count to ALL users
        result = await db.database["users"].update_many(
            {},  # Update all users
            {"$set": {"feature_usage_count": 5}}
        )
        
        return {
            "message": f"Added feature_usage_count to {result.modified_count} users",
            "modified_count": result.modified_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )

@auth_router.post("/verify-email")
async def verify_email_endpoint(token: str = None, code: str = None):
    """Verify HR email with token (from link) or code (6-char uppercase)"""
    from db import db
    from datetime import datetime, timedelta

    lookup_value = token or code
    if not lookup_value:
        raise HTTPException(status_code=400, detail="Token or code is required")

    # Find user by token (full token match or first 6 chars uppercase match)
    user = await db.database["users"].find_one({"verification_token": {"$exists": True}})
    
    # Try full token match
    user = await db.database["users"].find_one({"verification_token": lookup_value})
    
    # Try 6-char code match
    if not user and len(lookup_value) == 6:
        all_pending = db.database["users"].find({"user_status": "pending_verification", "verification_token": {"$exists": True}})
        async for pending_user in all_pending:
            stored_token = pending_user.get("verification_token", "")
            if stored_token[:6].upper() == lookup_value.upper():
                user = pending_user
                break

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    # Activate the account
    await db.database["users"].update_one(
        {"user_id": user["user_id"]},
        {"$set": {"user_status": "active", "is_verified": True},
         "$unset": {"verification_token": ""}}
    )

    return {"message": "Email verified successfully. Your HR account is now active.", "user_id": user["user_id"]}


@auth_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset token"""
    from auth_utils import generate_reset_token
    from datetime import timedelta
    from db import db
    from email_service import email_service
    
    user = await get_user_by_email(request.email)
    if not user:
        return {"message": "If email exists, reset link will be sent"}
    
    token = generate_reset_token()
    expire = datetime.utcnow() + timedelta(hours=1)
    
    await db.database["users"].update_one(
        {"email": request.email},
        {"$set": {"reset_token": token, "reset_token_expire": expire}}
    )
    
    # Send email
    user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "User"
    email_sent = email_service.send_password_reset_email(request.email, token, user_name)
    
    if not email_sent:
        logger.warning("Failed to send reset email for: %s", request.email)
    
    return {"message": "If email exists, reset link will be sent"}

@auth_router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password with token"""
    from db import db
    
    user = await db.database["users"].find_one({
        "reset_token": request.token,
        "reset_token_expire": {"$gt": datetime.utcnow()}
    })
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    success = await change_user_password(user["user_id"], request.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reset password")
    
    await db.database["users"].update_one(
        {"user_id": user["user_id"]},
        {"$unset": {"reset_token": "", "reset_token_expire": ""}}
    )
    
    return {"message": "Password reset successfully"}
