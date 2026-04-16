import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from auth_schemas import UserResponse
from google_auth import GoogleAuthService
from auth_db import create_user, get_user_by_email
from datetime import datetime

router = APIRouter()
google_auth = GoogleAuthService()

class GoogleSignInRequest(BaseModel):
    credential: str

class GoogleSignInResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/google-signin", response_model=GoogleSignInResponse)
async def google_signin(request: GoogleSignInRequest):
    """Handle Google Sign-In"""
    try:
        # Verify Google token
        google_user_info = google_auth.verify_google_token(request.credential)
        if not google_user_info:
            raise HTTPException(status_code=400, detail="Invalid Google token")
        
        # Check if user exists
        existing_user = await get_user_by_email(google_user_info['email'])
        
        if existing_user:
            # Update user info from Google
            from auth_db import update_user_profile
            update_data = {
                'first_name': google_user_info['first_name'],
                'last_name': google_user_info['last_name'],
                'last_active': datetime.utcnow(),
                'google_id': google_user_info['google_id'],
                'profile_picture': google_user_info.get('picture', ''),
                'is_verified': google_user_info.get('email_verified', False)
            }
            await update_user_profile(existing_user['user_id'], update_data)
            user = existing_user
        else:
            # Create new user
            user_data = {
                'email': google_user_info['email'],
                'first_name': google_user_info['first_name'],
                'last_name': google_user_info['last_name'],
                'user_type': 'candidate',  # Default to candidate
                'google_id': google_user_info['google_id'],
                'profile_picture': google_user_info.get('picture', ''),
                'is_verified': google_user_info.get('email_verified', False)
            }
            
            user = await create_user(user_data)
        
        # Generate JWT token
        jwt_token = google_auth.create_jwt_token({
            'user_id': user['user_id'],
            'email': user['email']
        })
        
        # Convert user to response format
        user_response = UserResponse(
            user_id=user['user_id'],
            email=user['email'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            user_type=user.get('user_type', 'candidate'),
            user_status=user.get('user_status', 'active'),
            user_plan=user.get('user_plan', 'F'),
            feature_usage_count=user.get('feature_usage_count', 5),
            profile_created_on=user['profile_created_on'],
            last_active=user['last_active'],
            match_analysis_count=user.get('match_analysis_count', 0),
            match_tailored_count=user.get('match_tailored_count', 0),
            mock_interview_count=user.get('mock_interview_count', 0),
            profile_completion_count=user.get('profile_completion_count', 0),
            profile_visits=user.get('profile_visits', 0),
            full_name=f"{user['first_name']} {user['last_name']}",
            is_active=user.get('is_active', True),
            created_at=user['profile_created_on'].isoformat(),
            updated_at=user['last_active'].isoformat() if user.get('last_active') else user['profile_created_on'].isoformat()
        )
        
        return GoogleSignInResponse(
            access_token=jwt_token,
            token_type="bearer",
            user=user_response
        )
        
    except Exception as e:
        logger.debug("Google sign-in error: %s ", e)
        raise HTTPException(status_code=500, detail="Google sign-in failed")