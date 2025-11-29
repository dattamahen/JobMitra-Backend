from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from database import get_database
from interview_prompts_collection import get_smart_prompt
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class UserProfileRequest(BaseModel):
    role: str
    experience_years: int
    skills: List[str]
    user_id: Optional[str] = None

class InterviewPromptResponse(BaseModel):
    prompt_template: str
    question_count: int
    difficulty: str
    role: str
    experience_level: str
    technology: str

@router.post("/get-interview-prompt", response_model=InterviewPromptResponse)
async def get_interview_prompt(user_profile: UserProfileRequest, db=Depends(get_database)):
    """
    Get smart interview prompt based on user profile
    """
    try:
        # Get smart prompt criteria
        criteria = get_smart_prompt(user_profile.dict())
        
        # Query database for matching prompt
        prompt_doc = db.interview_prompts.find_one({
            "role": criteria['role'],
            "experience_level": criteria['experience_level']
        })
        
        # Fallback to any role if specific not found
        if not prompt_doc:
            prompt_doc = db.interview_prompts.find_one({
                "experience_level": criteria['experience_level']
            })
        
        if not prompt_doc:
            raise HTTPException(status_code=404, detail="No suitable interview prompt found")
        
        return InterviewPromptResponse(
            prompt_template=prompt_doc["prompt_template"],
            question_count=prompt_doc["question_count"],
            difficulty=prompt_doc["difficulty"],
            role=prompt_doc["role"],
            experience_level=prompt_doc["experience_level"],
            technology=prompt_doc["technology"]
        )
        
    except Exception as e:
        logger.error(f"Error getting interview prompt: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get interview prompt")

@router.get("/interview-prompts")
async def list_interview_prompts(db=Depends(get_database)):
    """
    List all available interview prompts
    """
    try:
        prompts = list(db.interview_prompts.find({}, {"_id": 0}))
        return {"prompts": prompts}
    except Exception as e:
        logger.error(f"Error listing prompts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list prompts")