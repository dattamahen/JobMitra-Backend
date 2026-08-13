import logging

logger = logging.getLogger(__name__)

import asyncio
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from auth_schemas import UserResponse
from google_auth import GoogleAuthService
from auth_db import create_user, get_user_by_email, update_user_profile
from datetime import datetime
from config import settings

router = APIRouter()
google_auth = GoogleAuthService()

ADMIN_EMAIL = "renukadevi@jobmouka.com"


def _fire_failure_email(email: str, name: str, reason: str) -> None:
    try:
        from email_service import email_service
        asyncio.create_task(asyncio.to_thread(
            email_service.send_auth_failure_email, email, name, "google", reason
        ))
    except Exception as ex:
        logger.warning("Could not schedule failure notification: %s", ex)


class GoogleSignInRequest(BaseModel):
    credential: str

class GoogleSignInResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/google-signin", response_model=GoogleSignInResponse)
async def google_signin(request: GoogleSignInRequest):
    """Handle Google Sign-In"""
    google_user_info = None
    try:
        # Verify Google token
        google_user_info = google_auth.verify_google_token(request.credential)
        if not google_user_info:
            _fire_failure_email('unknown', '', 'Invalid Google token')
            raise HTTPException(status_code=400, detail="Invalid Google token")
        
        # Check if user exists
        existing_user = await get_user_by_email(google_user_info['email'])
        
        if existing_user:
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
                'user_type': 'candidate',
                'google_id': google_user_info['google_id'],
                'profile_picture': google_user_info.get('picture', ''),
                'is_verified': google_user_info.get('email_verified', False)
            }
            user = await create_user(user_data)
            # Send welcome email for first-time registration
            from email_service import email_service
            user_name = f"{google_user_info['first_name']} {google_user_info['last_name']}"
            asyncio.create_task(asyncio.to_thread(email_service.send_welcome_email, google_user_info['email'], user_name))
        
        # Generate JWT token
        jwt_token = google_auth.create_jwt_token({
            'user_id': user['user_id'],
            'email': user['email']
        })
        
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
            created_at=user['profile_created_on'].isoformat() + "Z",
            updated_at=user['last_active'].isoformat() + "Z" if user.get('last_active') else user['profile_created_on'].isoformat() + "Z"
        )
        
        return GoogleSignInResponse(
            access_token=jwt_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Google sign-in error: %s", e, exc_info=True)
        email = (google_user_info or {}).get('email', 'unknown')
        name = f"{(google_user_info or {}).get('first_name', '')} {(google_user_info or {}).get('last_name', '')}".strip()
        _fire_failure_email(email, name, str(e))
        raise HTTPException(status_code=500, detail=f"Google sign-in failed: {str(e)}")


class GoogleSignInCodeRequest(BaseModel):
    code: str
    redirect_uri: str

@router.post("/google-signin-code", response_model=GoogleSignInResponse)
async def google_signin_code(request: GoogleSignInCodeRequest):
    """Exchange Android OAuth authorization code for tokens and sign in"""
    google_user_info = None
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": request.code,
                    "client_id": settings.GOOGLE_ANDROID_CLIENT_ID,
                    "redirect_uri": request.redirect_uri,
                    "grant_type": "authorization_code",
                }
            )
            if token_response.status_code != 200:
                logger.error("Token exchange failed: %s", token_response.text)
                raise HTTPException(status_code=400, detail="Failed to exchange authorization code")

            token_data = token_response.json()
            id_token_str = token_data.get("id_token")
            if not id_token_str:
                raise HTTPException(status_code=400, detail="No ID token in response")

        google_user_info = google_auth.verify_google_token(id_token_str)
        if not google_user_info:
            raise HTTPException(status_code=400, detail="Invalid Google token")

        existing_user = await get_user_by_email(google_user_info['email'])
        if existing_user:
            await update_user_profile(existing_user['user_id'], {
                'first_name': google_user_info['first_name'],
                'last_name': google_user_info['last_name'],
                'last_active': datetime.utcnow(),
                'google_id': google_user_info['google_id'],
                'profile_picture': google_user_info.get('picture', ''),
                'is_verified': google_user_info.get('email_verified', False)
            })
            user = existing_user
        else:
            user = await create_user({
                'email': google_user_info['email'],
                'first_name': google_user_info['first_name'],
                'last_name': google_user_info['last_name'],
                'user_type': 'candidate',
                'google_id': google_user_info['google_id'],
                'profile_picture': google_user_info.get('picture', ''),
                'is_verified': google_user_info.get('email_verified', False)
            })

        jwt_token = google_auth.create_jwt_token({'user_id': user['user_id'], 'email': user['email']})

        return GoogleSignInResponse(
            access_token=jwt_token,
            token_type="bearer",
            user=UserResponse(
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
                created_at=user['profile_created_on'].isoformat() + "Z",
                updated_at=user['last_active'].isoformat() + "Z" if user.get('last_active') else user['profile_created_on'].isoformat() + "Z"
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Google sign-in code exchange error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Google sign-in failed: {str(e)}")
