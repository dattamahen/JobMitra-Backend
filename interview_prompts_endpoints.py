"""
Interview Prompts Endpoints
Uses file-based prompt_manager with strict JSON output enforcement.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from multi_llm_service import MultiLLMService
from prompt_manager import prompt_manager
from api_contracts import InterviewQuestionResponse
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
	interview_type: Optional[str] = "technical"


def _experience_label(years: int) -> str:
	if years <= 1: return "Entry-level (0-1 years) — focus on fundamentals and learning"
	if years <= 4: return "Mid-level (2-4 years) — focus on independent execution and ownership"
	if years <= 8: return "Senior (5-8 years) — focus on leadership, strategy, and cross-functional impact"
	return "Principal/Expert (9+ years) — focus on organizational influence and domain mastery"


def _build_question_prompt(system_prompt: str, user_details: dict, interview_type: str = "technical") -> str:
	"""Build a prompt combining the JSON system prompt with dynamic candidate context."""
	skills = user_details.get("skills", [])
	skills_str = ", ".join(skills) if skills else "General professional skills"
	experience_years = user_details.get("experience_years", 0)
	return f"""{system_prompt}

Candidate Profile:
- Role: {user_details.get("role", "Professional")}
- Experience Level: {_experience_label(experience_years)} ({experience_years} years)
- Skills to focus on: {skills_str}
- Interview Type: {interview_type}

IMPORTANT:
- Generate questions ONLY relevant to the above role and skills
- Treat each skill at face value based on its plain English meaning — do NOT reinterpret skill names through a technical lens
- Example: 'Event Coordination' means organizing and managing events (conferences, meetings, logistics) — NOT software event-driven architecture
- Example: 'Python' means the programming language — NOT the snake
- If the role and skills seem mismatched, trust the SKILLS over the role title when generating questions

STRICT OUTPUT RULES:
- Return ONLY a valid JSON object
- Format: {{"questions": ["question 1", "question 2", ...]}}
- Each question must be a single, concise string
- No markdown, no numbering, no explanations, no extra text
- Start your response with {{ and end with }}"""


def _parse_questions(content: str) -> List[str]:
	"""Parse LLM response into a clean list of question strings."""
	content = content.strip()

	# Strategy 1: Direct JSON parse
	try:
		content_clean = re.sub(r"^```(?:json)?\s*", "", content)
		content_clean = re.sub(r"\s*```$", "", content_clean).strip()
		data = json.loads(content_clean)
		questions = data.get("questions", [])
		if questions and isinstance(questions, list):
			return [q.get("question", str(q)) if isinstance(q, dict) else str(q) for q in questions]
	except (json.JSONDecodeError, AttributeError):
		pass

	# Strategy 2: Extract JSON object from mixed content
	try:
		match = re.search(r"\{[\s\S]*\"questions\"\s*:\s*\[[\s\S]*\][\s\S]*\}", content)
		if match:
			data = json.loads(match.group())
			questions = data.get("questions", [])
			if questions:
				return [q.get("question", str(q)) if isinstance(q, dict) else str(q) for q in questions]
	except (json.JSONDecodeError, AttributeError):
		pass

	# Strategy 3: Parse numbered list (1. Question\n2. Question)
	numbered = re.findall(r"^\s*\d+[\.\)]\s*(.+)", content, re.MULTILINE)
	if len(numbered) >= 3:
		return [q.strip().strip('"').strip("*") for q in numbered]

	# Strategy 4: Split by double newlines for paragraph-style questions
	paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and "?" in p]
	if len(paragraphs) >= 3:
		return paragraphs

	logger.warning("All parsing strategies failed, returning raw content")
	return [content]


@router.post("/get-interview-prompt")
async def get_interview_prompt(user_profile: UserProfileRequest):
	"""Get smart interview prompt based on user profile and generate questions"""
	try:
		prompt_category = "behavioral_interview_questions" if user_profile.interview_type == "behavioral" else "interview_questions"

		variant = prompt_manager.get_random(
			prompt_category,
			user_id=user_profile.user_id,
		)

		if user_profile.generate_questions:
			user_details = {
				"role": user_profile.role,
				"experience_years": user_profile.experience_years,
				"skills": user_profile.skills,
			}

			final_prompt = _build_question_prompt(
				variant.get("system_prompt", ""),
				user_details,
				user_profile.interview_type,
			)

			ai_response = await llm_service.generate(final_prompt, user_profile.ai_provider or "gemini")
			questions = _parse_questions(ai_response.get("content", ""))

			return InterviewQuestionResponse(
				session_id=str(uuid.uuid4()),
				questions=questions,
				question_count=len(questions),
				provider=ai_response["provider"],
				model=ai_response["model"],
				prompt_variant=variant.get("id", ""),
				prompt_style=variant.get("style"),
			).model_dump()
		else:
			return {
				"prompt": variant.get("system_prompt", ""),
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
