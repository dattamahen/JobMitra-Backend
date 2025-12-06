"""
Multi-AI Endpoints
FastAPI endpoints for multi-AI agent system
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from crew.crew_setup import run_multi_ai_query

router = APIRouter(tags=["Multi-AI"])


class MultiAIRequest(BaseModel):
	"""Request model for multi-AI query"""
	question: str


class MultiAIResponse(BaseModel):
	"""Response model for multi-AI query"""
	success: bool
	response: str
	providers_used: list[str]
	workflow: str
	note: Optional[str] = None
	error: Optional[str] = None


@router.post("/multi-ask", response_model=MultiAIResponse)
async def multi_ai_ask(request: MultiAIRequest):
	"""
	Process query using multi-AI agent system (ChatGPT + Gemini + Claude)
	
	Args:
		request: MultiAIRequest with question field
		
	Returns:
		MultiAIResponse: AI-generated response with metadata
	"""
	try:
		if not request.question or not request.question.strip():
			raise HTTPException(status_code=400, detail="Question cannot be empty")
		
		# Execute multi-AI workflow
		result = run_multi_ai_query(request.question)
		
		return MultiAIResponse(**result)
		
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail=f"Multi-AI processing failed: {str(e)}"
		)
