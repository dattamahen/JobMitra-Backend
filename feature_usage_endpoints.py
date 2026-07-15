"""
Feature Usage Tracking Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from typing import Optional
from db import db
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth_utils import verify_token
from auth_db import get_user_by_id
import jwt

router = APIRouter(prefix="/api/v1/features", tags=["Feature Usage"])
security = HTTPBearer()

# Get current user dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user = await get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Plan normalization
_PLAN_MAP = {'free': 'F', 'paid': 'P', 'subscribed': 'P', 'pro': 'S', 'premium': 'S'}
def normalize_plan(p: str) -> str:
    return _PLAN_MAP.get(str(p).lower(), p if p in ('F', 'P', 'S') else 'F')

# Schemas
class FeatureUsageResponse(BaseModel):
    plan: str
    remaining_count: int
    status: Literal["A", "X"]

class UseFeatureRequest(BaseModel):
    feature: str

class UseFeatureResponse(BaseModel):
    success: bool
    remaining_count: int
    status: Literal["A", "X"]
    message: Optional[str] = None

# Plan limits
PLAN_LIMITS = {
    "F": 5,
    "P": 15,
    "S": 35
}

@router.get("/usage", response_model=FeatureUsageResponse)
async def get_feature_usage(current_user: dict = Depends(get_current_user)):
    """Get current user's feature usage information"""
    try:
        plan = normalize_plan(current_user.get("user_plan", "F"))
        count = current_user.get("feature_usage_count", PLAN_LIMITS.get(plan, 5))
        usage_status = "A" if count > 0 else "X"
        
        return FeatureUsageResponse(
            plan=plan,
            remaining_count=count,
            status=usage_status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feature usage: {str(e)}"
        )

@router.post("/use", response_model=UseFeatureResponse)
async def use_feature(
    request: UseFeatureRequest,
    current_user: dict = Depends(get_current_user)
):
    """Use a paid feature (decrements count)"""
    try:
        user_id = current_user["user_id"]
        current_count = current_user.get("feature_usage_count", 0)
        
        # Check if user can use features
        if current_count <= 0:
            return UseFeatureResponse(
                success=False,
                remaining_count=0,
                status="X",
                message="No more paid features available"
            )
        
        # Decrement count
        new_count = max(0, current_count - 1)
        new_status = "A" if new_count > 0 else "X"
        
        # Update user record
        await db.database["users"].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "feature_usage_count": new_count,
                    "updated_at": datetime.utcnow().isoformat() + "Z",
                    "last_active": datetime.utcnow()
                }
            }
        )
        
        # Log the usage
        await db.database["feature_usage_log"].insert_one({
            "user_id": user_id,
            "feature_name": request.feature,
            "used_at": datetime.utcnow(),
            "remaining_count": new_count,
            "user_plan": current_user.get("user_plan", "F")
        })
        
        return UseFeatureResponse(
            success=True,
            remaining_count=new_count,
            status=new_status,
            message="Feature used successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error using feature: {str(e)}"
        )