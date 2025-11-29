from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from db_simple import db
from interview_prompts_collection import get_smart_prompt
from ai_interview_service import AIInterviewService
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)
ai_service = AIInterviewService()

class UserProfileRequest(BaseModel):
    role: str
    experience_years: int
    skills: List[str]
    user_id: Optional[str] = None
    ai_provider: Optional[str] = "openai"
    generate_questions: Optional[bool] = True

class InterviewPromptResponse(BaseModel):
    prompt_template: str
    question_count: int
    difficulty: str
    role: str
    experience_level: str

class AIInterviewResponse(BaseModel):
    session_id: str
    questions: str
    provider: str
    prompt_used: str
    difficulty: str

@router.post("/get-interview-prompt")
async def get_interview_prompt(user_profile: UserProfileRequest):
    """
    Get smart interview prompt based on user profile
    """
    try:
        print(f"Received user profile: {user_profile.dict()}")
        
        # Get smart prompt criteria
        criteria = get_smart_prompt(user_profile.dict())
        print(f"Generated criteria: {criteria}")
        
        # Check database connection
        if not db.database:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # Query database for matching prompt
        prompt_doc = await db.database.interview_prompts.find_one({
            "role": criteria['role'],
            "experience_level": criteria['experience_level']
        })
        print(f"Found prompt with exact match: {prompt_doc is not None}")
        
        # Fallback to any role if specific not found
        if not prompt_doc:
            prompt_doc = await db.database.interview_prompts.find_one({
                "experience_level": criteria['experience_level']
            })
            print(f"Found prompt with fallback: {prompt_doc is not None}")
        
        if not prompt_doc:
            raise HTTPException(status_code=404, detail="No suitable interview prompt found")
        
        # Print prompt to console
        print("\n" + "="*80)
        print(f"INTERVIEW PROMPT SELECTED:")
        print(f"Role: {prompt_doc['role']}")
        print(f"Experience Level: {prompt_doc['experience_level']}")
        print(f"Difficulty: {prompt_doc['difficulty']}")
        print(f"Question Count: {prompt_doc['question_count']}")
        print("\nPROMPT TEMPLATE:")
        print(prompt_doc['prompt_template'])
        print("="*80 + "\n")
        
        # If AI generation requested, generate questions
        if user_profile.generate_questions:
            try:
                ai_response = await ai_service.generate_interview_questions(
                    prompt_doc["prompt_template"], 
                    user_profile.ai_provider
                )
                
                import uuid
                session_id = str(uuid.uuid4())
                
                print("\n" + "="*80)
                print(f"AI INTERVIEW STARTED - Session: {session_id}")
                print(f"Provider: {ai_response['provider'].upper()}")
                print(f"Difficulty: {prompt_doc['difficulty']}")
                print("\nGENERATED QUESTIONS:")
                print(ai_response['questions'])
                print("="*80 + "\n")
                
                return {
                    "session_id": session_id,
                    "questions": ai_response['questions'],
                    "provider": ai_response['provider'],
                    "prompt_used": prompt_doc['prompt_template'],
                    "difficulty": prompt_doc['difficulty'],
                    "role": prompt_doc['role'],
                    "experience_level": prompt_doc['experience_level']
                }
            except Exception as e:
                print(f"\n=== AI GENERATION ERROR ===")
                print(f"Error: {str(e)}")
                print(f"API Key exists: {bool(os.getenv('OPENAI_API_KEY'))}")
                print(f"API Key length: {len(os.getenv('OPENAI_API_KEY', ''))}")
                print("=========================\n")
                logger.error(f"AI generation failed: {str(e)}")
                # Fallback to mock response
                import uuid
                session_id = str(uuid.uuid4())
                mock_questions = f"Fallback Questions for {prompt_doc['experience_level']} {prompt_doc['role']}:\n1. Tell me about yourself\n2. What are your strengths?\n3. Describe a challenging project"
                
                return {
                    "session_id": session_id,
                    "questions": mock_questions,
                    "provider": "fallback",
                    "prompt_used": prompt_doc['prompt_template'],
                    "difficulty": prompt_doc['difficulty'],
                    "role": prompt_doc['role'],
                    "experience_level": prompt_doc['experience_level']
                }
        else:
            print("\n" + "="*80)
            print(f"INTERVIEW PROMPT SELECTED:")
            print(f"Role: {prompt_doc['role']}")
            print(f"Experience Level: {prompt_doc['experience_level']}")
            print(f"Difficulty: {prompt_doc['difficulty']}")
            print(f"Question Count: {prompt_doc['question_count']}")
            print("\nPROMPT TEMPLATE:")
            print(prompt_doc['prompt_template'])
            print("="*80 + "\n")
            
            return {
                "prompt_template": prompt_doc["prompt_template"],
                "question_count": prompt_doc["question_count"],
                "difficulty": prompt_doc["difficulty"],
                "role": prompt_doc["role"],
                "experience_level": prompt_doc["experience_level"]
            }
        
    except Exception as e:
        logger.error(f"Error getting interview prompt: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get interview prompt")

@router.get("/interview-prompts")
async def list_interview_prompts():
    """
    List all available interview prompts
    """
    try:
        prompts = await db.database.interview_prompts.find({}, {"_id": 0}).to_list(length=None)
        return {"prompts": prompts}
    except Exception as e:
        logger.error(f"Error listing prompts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list prompts")

