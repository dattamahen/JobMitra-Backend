"""
Dynamic AI Endpoints for Interview and CV Tailoring
Uses file-based prompt_manager instead of MongoDB for prompt selection.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from crew.workflows import run_interview_workflow, run_cv_tailoring_workflow, evaluate_interview_answers
from prompt_manager import prompt_manager

router = APIRouter(tags=["Dynamic-AI"])


class UserProfile(BaseModel):
	name: str
	experience: int
	skills: List[str]


class InterviewRequest(BaseModel):
	user_profile: UserProfile


class InterviewAnswerRequest(BaseModel):
	user_profile: UserProfile
	questions: List[str]
	answers: List[str]


class CVTailorRequest(BaseModel):
	user_details: dict
	job_description: str


@router.post("/interview/generate")
async def generate_interview_questions(request: InterviewRequest):
	"""Generate interview questions based on user profile"""
	try:
		question_variant = prompt_manager.get_random("interview_questions")
		eval_variant = prompt_manager.get_random("interview_evaluation")

		prompts = {
			"question_prompt": question_variant.get("system_prompt", ""),
			"eval_prompt": eval_variant.get("system_prompt", ""),
		}

		user_profile = {
			"name": request.user_profile.name,
			"experience": request.user_profile.experience,
			"skills": request.user_profile.skills,
		}

		result = await run_interview_workflow(user_profile, prompts)

		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error"))

		return result

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Interview generation failed: {str(e)}")


@router.post("/interview/evaluate")
async def evaluate_interview(request: InterviewAnswerRequest):
	"""Evaluate candidate's interview answers"""
	try:
		question_variant = prompt_manager.get_random("interview_questions")
		eval_variant = prompt_manager.get_random("interview_evaluation")

		prompts = {
			"question_prompt": question_variant.get("system_prompt", ""),
			"eval_prompt": eval_variant.get("system_prompt", ""),
		}

		user_profile = {
			"name": request.user_profile.name,
			"experience": request.user_profile.experience,
			"skills": request.user_profile.skills,
		}

		result = await evaluate_interview_answers(
			request.questions,
			request.answers,
			user_profile,
			prompts,
		)

		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error"))

		return result

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/cv/tailor")
async def tailor_cv(request: CVTailorRequest):
	"""Tailor CV for job description"""
	try:
		tailor_variant = prompt_manager.get_random("resume_tailoring")
		eval_variant = prompt_manager.get_random("resume_validation")

		prompts = {
			"cv_tailor": tailor_variant.get("system_prompt", ""),
			"cv_evaluator": eval_variant.get("system_prompt", ""),
		}

		result = await run_cv_tailoring_workflow(
			request.user_details,
			request.job_description,
			prompts,
		)

		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error"))

		return result

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"CV tailoring failed: {str(e)}")
