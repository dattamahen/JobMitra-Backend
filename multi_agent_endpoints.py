from fastapi import APIRouter, HTTPException
from typing import List
import os

router = APIRouter(tags=["Multi-Agent-Interview"])

@router.get("/multi-agent/providers")
async def list_providers():
	"""List available LLM providers and their status. All route through Gemini internally."""
	gemini_available = bool(os.getenv("GEMINI_API_KEY"))
	return {
		"providers": [
			{
				"name": "openai",
				"model": "gpt-4",
				"available": gemini_available
			},
			{
				"name": "gemini",
				"model": "gemini-3.5-flash",
				"available": gemini_available
			},
			{
				"name": "claude",
				"model": "claude-3-sonnet",
				"available": gemini_available
			}
		]
	}
