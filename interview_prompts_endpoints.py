from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from db_simple import db
from interview_prompts_collection import get_smart_prompt, get_mock_interview_prompt_template
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
		
		# First try to find the universal question_generator prompt
		prompt_doc = await db.database.interview_prompts.find_one({
			"experience_level": "any",
			"prompt_type": "question_generator"
		})
		
		# Fallback to experience-specific prompts
		if not prompt_doc:
			prompt_doc = await db.database.interview_prompts.find_one({
				"experience_level": criteria['experience_level']
			})
		
		if not prompt_doc:
			raise HTTPException(status_code=404, detail="No suitable interview prompt found")
		
		if user_profile.generate_questions:
			try:
				print(f"Backend using: gemini (ignoring UI request for {user_profile.ai_provider})")
				
				# Use the prompt_template from database
				prompt_template = prompt_doc.get('prompt_template', '')
				skills_str = ", ".join(user_profile.skills)
				
				# Build user details JSON for the prompt
				user_details = {
					"role": user_profile.role,
					"experience_years": user_profile.experience_years,
					"skills": user_profile.skills,
					"generate_questions": user_profile.generate_questions
				}
				
				final_prompt = f"{prompt_template}\n\nUser Details: {user_details}"
				
				ai_response = await llm_service.generate(
					final_prompt, 
					"gemini"
				)
				
				# Parse the JSON response to extract questions array
				import json
				import re
				try:
					content = ai_response['content']
					# Remove markdown code blocks if present
					content = re.sub(r'^```json\s*', '', content)
					content = re.sub(r'\s*```$', '', content)
					content = content.strip()
					
					questions_data = json.loads(content)
					questions_list = questions_data.get('questions', [])
					
					# Extract just the question text from each object
					if questions_list and isinstance(questions_list[0], dict):
						questions_array = [q.get('question', str(q)) for q in questions_list]
					else:
						questions_array = questions_list
				except:
					questions_array = [ai_response['content']]
				
				return {
					"session_id": str(uuid.uuid4()),
					"questions": questions_array,
					"provider": ai_response['provider'],
					"model": ai_response['model']
				}
			except Exception as e:
				logger.error(f"AI generation failed: {str(e)}")
				raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")
		else:
			return {
				"prompt": prompt_doc.get("prompt_template", ""),
				"experience_level": prompt_doc["experience_level"],
				"prompt_type": prompt_doc.get("prompt_type", "N/A")
			}
	except Exception as e:
		logger.error(f"Error: {str(e)}")
		import traceback
		traceback.print_exc()
		raise HTTPException(status_code=500, detail=f"Failed to get interview prompt: {str(e)}")

@router.get("/interview-prompts")
async def list_interview_prompts():
	"""List all available interview prompts"""
	try:
		prompts = await db.database.interview_prompts.find({}, {"_id": 0}).to_list(length=None)
		return {"prompts": prompts}
	except Exception as e:
		logger.error(f"Error listing prompts: {str(e)}")
		raise HTTPException(status_code=500, detail="Failed to list prompts")
