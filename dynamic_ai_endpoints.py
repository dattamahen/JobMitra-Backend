"""
Dynamic AI Endpoints for Interview and CV Tailoring
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from crew.workflows import run_interview_workflow, run_cv_tailoring_workflow, evaluate_interview_answers
from db_simple import db

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


async def get_prompt_from_db(role_type: str, experience_level: str, prompt_type: str):
	"""Fetch specific prompt from MongoDB"""
	try:
		collection = db.database["interview_prompts"]
		prompt_doc = await collection.find_one({
			"role_type": role_type,
			"experience_level": experience_level,
			"prompt_type": prompt_type
		})
		
		if prompt_doc:
			return prompt_doc.get("prompt", "")
		
		return "You are an expert interviewer."
	except:
		return "You are an expert interviewer."


@router.post("/interview/generate")
async def generate_interview_questions(request: InterviewRequest):
	"""Generate interview questions based on user profile"""
	try:
		experience = request.user_profile.experience
		skills = request.user_profile.skills
		is_tech = any(s.lower() in ['python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 'mongodb', 'aws', 'docker', 'kubernetes'] for s in skills)
		
		role_type = "technical" if is_tech else "general"
		
		if experience <= 1:
			exp_level = "0-1"
		elif experience <= 3:
			exp_level = "1-3"
		elif experience <= 7:
			exp_level = "3-7"
		else:
			exp_level = "7+"
		
		prompts = {
			"question_prompt": await get_prompt_from_db(role_type, exp_level, "question_generator"),
			"eval_prompt": await get_prompt_from_db(role_type, exp_level, "answer_evaluator")
		}
		
		user_profile = {
			"name": request.user_profile.name,
			"experience": request.user_profile.experience,
			"skills": request.user_profile.skills
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
		experience = request.user_profile.experience
		skills = request.user_profile.skills
		is_tech = any(s.lower() in ['python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 'mongodb', 'aws', 'docker', 'kubernetes'] for s in skills)
		
		role_type = "technical" if is_tech else "general"
		
		if experience <= 1:
			exp_level = "0-1"
		elif experience <= 3:
			exp_level = "1-3"
		elif experience <= 7:
			exp_level = "3-7"
		else:
			exp_level = "7+"
		
		prompts = {
			"question_prompt": await get_prompt_from_db(role_type, exp_level, "question_generator"),
			"eval_prompt": await get_prompt_from_db(role_type, exp_level, "answer_evaluator")
		}
		
		user_profile = {
			"name": request.user_profile.name,
			"experience": request.user_profile.experience,
			"skills": request.user_profile.skills
		}
		
		result = await evaluate_interview_answers(
			request.questions,
			request.answers,
			user_profile,
			prompts
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
		prompts = {
			"cv_tailor": await get_prompt_from_db("cv", "all", "cv_tailor"),
			"cv_evaluator": await get_prompt_from_db("cv", "all", "cv_evaluator")
		}
		
		result = await run_cv_tailoring_workflow(
			request.user_details,
			request.job_description,
			prompts
		)
		
		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error"))
		
		return result
		
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"CV tailoring failed: {str(e)}")


@router.get("/prompts")
async def get_agent_prompts():
	"""Get all prompts from database"""
	try:
		collection = db.database["interview_prompts"]
		prompts = await collection.find().to_list(None)
		
		for prompt in prompts:
			prompt["_id"] = str(prompt["_id"])
		
		return {"success": True, "prompts": prompts}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompts/update")
async def update_agent_prompts(prompt_data: dict):
	"""Update specific prompt in database"""
	try:
		collection = db.database["interview_prompts"]
		
		await collection.update_one(
			{
				"role_type": prompt_data.get("role_type"),
				"experience_level": prompt_data.get("experience_level"),
				"prompt_type": prompt_data.get("prompt_type")
			},
			{"$set": {"prompt": prompt_data.get("prompt")}},
			upsert=True
		)
		
		return {"success": True, "message": "Prompt updated"}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
