"""
Interview Prompts Endpoints
Uses file-based prompt_manager instead of MongoDB for prompt selection.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from multi_llm_service import MultiLLMService
from prompt_manager import prompt_manager
import logging
import json
import re
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
	"""Get smart interview prompt based on user profile and generate questions"""
	try:
		variant = prompt_manager.get_random(
			"interview_questions",
			user_id=user_profile.user_id,
		)
		system_prompt = variant.get("system_prompt", "")

		if user_profile.generate_questions:
			user_details = {
				"role": user_profile.role,
				"experience_years": user_profile.experience_years,
				"skills": user_profile.skills,
				"generate_questions": True,
			}

			final_prompt = f"{system_prompt}\n\nUser Details: {json.dumps(user_details)}"

			ai_response = await llm_service.generate(final_prompt, "gemini")

			try:
				content = ai_response["content"]
				content = re.sub(r"^```json\s*", "", content)
				content = re.sub(r"\s*```$", "", content)
				content = content.strip()

				questions_data = json.loads(content)
				questions_list = questions_data.get("questions", [])

				if questions_list and isinstance(questions_list[0], dict):
					questions_array = [q.get("question", str(q)) for q in questions_list]
				else:
					questions_array = questions_list
			except Exception:
				questions_array = [ai_response["content"]]

			return {
				"session_id": str(uuid.uuid4()),
				"questions": questions_array,
				"provider": ai_response["provider"],
				"model": ai_response["model"],
				"prompt_variant": variant.get("id"),
			}
		else:
			return {
				"prompt": system_prompt,
				"prompt_variant": variant.get("id"),
				"style": variant.get("style"),
			}

	except Exception as e:
		logger.error(f"Error: {str(e)}")
		import traceback
		traceback.print_exc()
		raise HTTPException(status_code=500, detail=f"Failed to get interview prompt: {str(e)}")


@router.get("/interview-prompts")
async def list_interview_prompts():
	"""List all available interview prompt variants"""
	categories = prompt_manager.list_categories()
	result = {}
	for cat in categories:
		result[cat] = prompt_manager.list_variants(cat)
	return {"prompts": result}
