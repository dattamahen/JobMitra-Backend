"""
Simple AI Endpoints - Direct OpenAI calls
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
from openai import OpenAI
from db_simple import db

router = APIRouter(tags=["AI-Interview"])

def get_openai_client():
	"""Get OpenAI client instance"""
	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
	return OpenAI(api_key=api_key)


class InterviewRequest(BaseModel):
	role: str
	experience_years: int
	skills: List[str]
	user_id: str
	generate_questions: bool = True
	ai_provider: str = "openai"


class InterviewAnswerRequest(BaseModel):
	role: str
	experience_years: int
	skills: List[str]
	user_id: str
	questions: List[str]
	answers: List[str]
	ai_provider: str = "openai"


async def get_prompt_from_db(role_type: str, experience_level: str, prompt_type: str):
	"""Fetch prompt from MongoDB"""
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
	"""Generate interview questions"""
	try:
		experience = request.experience_years
		skills = request.skills
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
		
		prompt_template = await get_prompt_from_db(role_type, exp_level, "question_generator")
		
		job_profile = f"Role: {request.role}, Experience: {experience} years, Skills: {', '.join(skills)}"
		prompt = prompt_template.format(job_profile=job_profile)
		
		client = get_openai_client()
		response = client.chat.completions.create(
			model="gpt-4",
			messages=[{"role": "user", "content": prompt}],
			temperature=0.7
		)
		
		return {
			"success": True,
			"user_id": request.user_id,
			"questions": response.choices[0].message.content,
			"role_type": role_type,
			"experience_level": exp_level,
			"ai_provider": request.ai_provider
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@router.post("/interview/evaluate")
async def evaluate_interview(request: InterviewAnswerRequest):
	"""Evaluate interview answers"""
	try:
		experience = request.experience_years
		skills = request.skills
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
		
		prompt_template = await get_prompt_from_db(role_type, exp_level, "answer_evaluator")
		
		job_profile = f"Role: {request.role}, Experience: {experience} years, Skills: {', '.join(skills)}"
		qa_pairs = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(request.questions, request.answers))])
		
		prompt = prompt_template.format(
			candidate_answer=qa_pairs,
			interview_question="Multiple questions",
			job_profile=job_profile
		)
		
		client = get_openai_client()
		response = client.chat.completions.create(
			model="gpt-4",
			messages=[{"role": "user", "content": prompt}],
			temperature=0.7
		)
		
		return {
			"success": True,
			"user_id": request.user_id,
			"evaluation": response.choices[0].message.content,
			"role_type": role_type,
			"experience_level": exp_level,
			"ai_provider": request.ai_provider
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@router.get("/prompts")
async def get_all_prompts():
	"""Get all prompts"""
	try:
		collection = db.database["interview_prompts"]
		prompts = await collection.find().to_list(None)
		
		for prompt in prompts:
			prompt["_id"] = str(prompt["_id"])
		
		return {"success": True, "prompts": prompts}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
