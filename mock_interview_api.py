from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

class InterviewQuestion(BaseModel):
	id: str
	question: str
	type: str

class StartInterviewRequest(BaseModel):
	interview_type: str
	difficulty: Optional[str] = "medium"
	company: Optional[str] = None

class InterviewSession(BaseModel):
	session_id: str
	questions: List[InterviewQuestion]
	created_at: datetime

class SubmitAnswerRequest(BaseModel):
	session_id: str
	question_id: str
	answer: str

class EvaluateInterviewRequest(BaseModel):
	session_id: str
	answers: List[dict]

class InterviewEvaluation(BaseModel):
	session_id: str
	overall_score: int
	feedback: str
	question_scores: List[dict]

# In-memory storage for sessions
interview_sessions = {}

@router.post("/api/v1/mock-interview/start", response_model=InterviewSession)
async def start_interview(request: StartInterviewRequest):
	"""Start a new mock interview session - Use /api/v1/get-interview-prompt instead"""
	raise HTTPException(
		status_code=410, 
		detail="This endpoint is deprecated. Use /api/v1/get-interview-prompt with AI-generated questions instead."
	)

@router.post("/api/v1/mock-interview/submit-answer")
async def submit_answer(request: SubmitAnswerRequest):
	"""Submit answer for a specific question"""
	try:
		if request.session_id not in interview_sessions:
			raise HTTPException(status_code=404, detail="Interview session not found")
		
		interview_sessions[request.session_id]["answers"][request.question_id] = request.answer
		
		return {"message": "Answer submitted successfully"}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error submitting answer: {str(e)}")

@router.post("/api/v1/mock-interview/evaluate", response_model=InterviewEvaluation)
async def evaluate_interview(request: EvaluateInterviewRequest):
	"""Evaluate the complete interview - Use /api/v1/evaluate-interview instead"""
	raise HTTPException(
		status_code=410,
		detail="This endpoint is deprecated. Use /api/v1/evaluate-interview with AI evaluation instead."
	)
