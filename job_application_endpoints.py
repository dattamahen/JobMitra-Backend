"""
Public job application endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel

from job_application_db import job_application_db
from auth_utils import verify_token
from auth_db import get_user_by_id

# Create router
application_router = APIRouter(prefix="/applications", tags=["Job Applications"])
security = HTTPBearer()

class JobApplicationRequest(BaseModel):
    job_id: str
    cover_letter: Optional[str] = None

# Dependency to get current authenticated user
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
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@application_router.post("/apply")
async def apply_for_job(
    application_request: JobApplicationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Apply for a job"""
    try:
        user_id = current_user["user_id"]
        application_id = await job_application_db.apply_for_job(
            application_request.job_id,
            user_id,
            application_request.cover_letter
        )
        
        return {
            "message": "Application submitted successfully",
            "application_id": application_id
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit application: {str(e)}"
        )