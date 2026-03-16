from fastapi import APIRouter, HTTPException
from typing import List
import os

router = APIRouter(tags=["Multi-Agent-Interview"])

@router.get("/multi-agent/providers")
async def list_providers():
	"""List available LLM providers and their status"""
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
