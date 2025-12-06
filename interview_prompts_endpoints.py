from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from db_simple import db
from interview_prompts_collection import get_smart_prompt
from multi_llm_service import MultiLLMService
import logging
import os
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)
llm_service = MultiLLMService()

class UserProfileRequest(BaseModel):
	role: str
	experience_years: int
	skills: List[str]
	user_id: Optional[str] = None
	ai_provider: Optional[str] = "gemini"
	generate_questions: Optional[bool] = True

@router.post("/get-interview-prompt")
async def get_interview_prompt(user_profile: UserProfileRequest):
	"""Get smart interview prompt based on user profile"""
	try:
		print(f"Received user profile: {user_profile.dict()}")
		
		criteria = get_smart_prompt(user_profile.dict())
		print(f"Generated criteria: {criteria}")
		
		if db.database is None:
			raise HTTPException(status_code=500, detail="Database not connected")
		
		prompt_doc = await db.database.interview_prompts.find_one({
			"role_type": criteria['role_type'],
			"experience_level": criteria['experience_level'],
			"prompt_type": "question_generator"
		})
		
		if not prompt_doc:
			prompt_doc = await db.database.interview_prompts.find_one({
				"experience_level": criteria['experience_level'],
				"prompt_type": "question_generator"
			})
		
		if not prompt_doc:
			raise HTTPException(status_code=404, detail="No suitable interview prompt found")
		
		if user_profile.generate_questions:
			try:
				# Backend always uses Gemini (working and free)
				print(f"Backend using: gemini (ignoring UI request for {user_profile.ai_provider})")
				
				# Inject user skills into prompt with strict formatting
				base_prompt = prompt_doc.get("prompt", "")
				skills_str = ", ".join(user_profile.skills)
				customized_prompt = f"{base_prompt}\n\nUser's Skills: {skills_str}\nUser's Role: {user_profile.role}\nUser's Experience: {user_profile.experience_years} years\n\nQUESTION REQUIREMENTS:\n- Test BOTH basic concepts AND advanced core concepts of each skill\n- Cover fundamental understanding and deep technical knowledge\n- Include practical scenario-based questions\n\nIMPORTANT OUTPUT FORMAT:\n- Generate ONLY the interview questions\n- Number each question (1., 2., 3., etc.)\n- Do NOT include greetings, introductions, or feedback\n- Do NOT include explanations or additional text\n- Each question should be on a new line"
				
				ai_response = await llm_service.generate(
					customized_prompt, 
					"gemini"
				)
				
				return {
					"session_id": str(uuid.uuid4()),
					"questions": ai_response['content'],
					"provider": ai_response['provider'],
					"model": ai_response['model'],
					"prompt_used": prompt_doc.get('prompt', ''),
					"role_type": prompt_doc.get('role_type', 'N/A'),
					"experience_level": prompt_doc['experience_level']
				}
			except Exception as e:
				logger.error(f"AI generation failed: {str(e)}")
				raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")
		else:
			return {
				"prompt": prompt_doc.get("prompt", ""),
				"role_type": prompt_doc.get("role_type", "N/A"),
				"experience_level": prompt_doc["experience_level"],
				"prompt_type": "question_generator"
			}
	except Exception as e:
		logger.error(f"Error: {str(e)}")
		raise HTTPException(status_code=500, detail="Failed to get interview prompt")

@router.post("/evaluate-interview")
async def evaluate_interview(user_profile: UserProfileRequest):
	"""Evaluate interview answers based on user profile"""
	try:
		criteria = get_smart_prompt(user_profile.dict())
		
		if db.database is None:
			raise HTTPException(status_code=500, detail="Database not connected")
		
		prompt_doc = await db.database.interview_prompts.find_one({
			"role_type": criteria['role_type'],
			"experience_level": criteria['experience_level'],
			"prompt_type": "answer_evaluator"
		})
		
		if not prompt_doc:
			prompt_doc = await db.database.interview_prompts.find_one({
				"experience_level": criteria['experience_level'],
				"prompt_type": "answer_evaluator"
			})
		
		if not prompt_doc:
			raise HTTPException(status_code=404, detail="No suitable evaluator prompt found")
		
		return {
			"success": True,
			"prompt": prompt_doc.get("prompt", ""),
			"role_type": prompt_doc.get("role_type", "N/A"),
			"experience_level": prompt_doc["experience_level"],
			"prompt_type": "answer_evaluator"
		}
	except Exception as e:
		logger.error(f"Error: {str(e)}")
		raise HTTPException(status_code=500, detail="Failed to get evaluator prompt")

@router.get("/interview-prompts")
async def list_interview_prompts():
	"""List all available interview prompts"""
	try:
		prompts = await db.database.interview_prompts.find({}, {"_id": 0}).to_list(length=None)
		return {"prompts": prompts}
	except Exception as e:
		logger.error(f"Error listing prompts: {str(e)}")
		raise HTTPException(status_code=500, detail="Failed to list prompts")
