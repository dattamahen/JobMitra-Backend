"""
Multi-Agent Interview System Endpoints
Supports OpenAI, Gemini, and Claude
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from db_simple import db
from interview_prompts_collection import get_smart_prompt
from multi_llm_service import MultiLLMService
import uuid

router = APIRouter(tags=["Multi-Agent-Interview"])
llm_service = MultiLLMService()

class InterviewGenerateRequest(BaseModel):
	role: str
	experience_years: int
	skills: List[str]
	user_id: str
	ai_provider: str = "gemini"  # openai, gemini, claude

class InterviewEvaluateRequest(BaseModel):
	role: str
	experience_years: int
	skills: List[str]
	user_id: str
	questions: List[str]
	answers: List[str]
	ai_provider: str = "gemini"

@router.post("/multi-agent/generate")
async def generate_questions(request: InterviewGenerateRequest):
	"""Generate interview questions using selected LLM provider"""
	try:
		# Smart provider fallback: Use Gemini if OpenAI unavailable
		import os
		original_provider = request.ai_provider
		if request.ai_provider == "openai":
			if not os.getenv("OPENAI_API_KEY") or not os.getenv("OPENAI_API_KEY").startswith("sk-"):
				request.ai_provider = "gemini"
				print(f"Switching from OpenAI to Gemini (OpenAI unavailable)")
		
		# Get criteria
		criteria = get_smart_prompt(request.dict())
		
		# Get prompt from database
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
			raise HTTPException(status_code=404, detail="No prompt found")
		
		# Format prompt with job profile and strict output format
		job_profile = f"Role: {request.role}, Experience: {request.experience_years} years, Skills: {', '.join(request.skills)}"
		base_prompt = prompt_doc.get('prompt', '').format(job_profile=job_profile)
		prompt = f"{base_prompt}\n\nQUESTION REQUIREMENTS:\n- Test BOTH basic concepts AND advanced core concepts of each skill: {', '.join(request.skills)}\n- Cover fundamental understanding and deep technical knowledge\n- Include practical scenario-based questions\n\nIMPORTANT OUTPUT FORMAT:\n- Generate ONLY the interview questions\n- Number each question (1., 2., 3., etc.)\n- Do NOT include greetings, introductions, or feedback\n- Do NOT include explanations or additional text\n- Each question should be on a new line"
		
		# Generate using selected provider
		response = await llm_service.generate(prompt, request.ai_provider)
		
		return {
			"success": True,
			"session_id": str(uuid.uuid4()),
			"user_id": request.user_id,
			"questions": response['content'],
			"provider": response['provider'],
			"model": response['model'],
			"role_type": criteria['role_type'],
			"experience_level": criteria['experience_level'],
			"original_provider_requested": original_provider
		}
	
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")

@router.post("/multi-agent/evaluate")
async def evaluate_answers(request: InterviewEvaluateRequest):
	"""Evaluate interview answers using selected LLM provider"""
	try:
		# Smart provider fallback: Use Gemini if OpenAI unavailable
		import os
		original_provider = request.ai_provider
		if request.ai_provider == "openai":
			if not os.getenv("OPENAI_API_KEY") or not os.getenv("OPENAI_API_KEY").startswith("sk-"):
				request.ai_provider = "gemini"
				print(f"Switching from OpenAI to Gemini (OpenAI unavailable)")
		
		# Get criteria
		criteria = get_smart_prompt(request.dict())
		
		# Get evaluator prompt from database
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
			raise HTTPException(status_code=404, detail="No evaluator prompt found")
		
		# Format prompt
		job_profile = f"Role: {request.role}, Experience: {request.experience_years} years, Skills: {', '.join(request.skills)}"
		qa_pairs = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(request.questions, request.answers))])
		
		prompt = prompt_doc.get('prompt', '').format(
			candidate_answer=qa_pairs,
			interview_question="Multiple questions",
			job_profile=job_profile
		)
		
		# Evaluate using selected provider
		response = await llm_service.generate(prompt, request.ai_provider)
		
		return {
			"success": True,
			"user_id": request.user_id,
			"evaluation": response['content'],
			"provider": response['provider'],
			"model": response['model'],
			"role_type": criteria['role_type'],
			"experience_level": criteria['experience_level'],
			"original_provider_requested": original_provider
		}
	
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")

@router.get("/multi-agent/providers")
async def list_providers():
	"""List available LLM providers and their status"""
	import os
	return {
		"providers": [
			{
				"name": "openai",
				"model": "gpt-4",
				"available": bool(os.getenv("OPENAI_API_KEY"))
			},
			{
				"name": "gemini",
				"model": "gemini-1.5-flash",
				"available": bool(os.getenv("GEMINI_API_KEY"))
			},
			{
				"name": "claude",
				"model": "claude-3-sonnet",
				"available": bool(os.getenv("ANTHROPIC_API_KEY"))
			}
		]
	}
