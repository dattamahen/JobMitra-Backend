import logging
logger = logging.getLogger(__name__)

import logging
import asyncio
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
from config import settings
from prompt_manager import prompt_manager

logger = logging.getLogger(__name__)

MODEL = "gemini-2.0-flash-lite"

class AIInterviewService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        self._client = genai.Client(api_key=api_key) if api_key else None
    
    async def generate_interview_questions(self, prompt_template: str, ai_provider: str = 'openai') -> Dict[str, Any]:
        """Generate interview questions using Gemini (all providers route through Gemini)"""
        try:
            return await self._generate_with_gemini(prompt_template, ai_provider)
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")
    
    async def _generate_with_gemini(self, prompt: str, branded_provider: str = 'openai') -> Dict[str, Any]:
        """Generate questions using Gemini internally"""
        if not self._client:
            raise Exception("GEMINI_API_KEY not found")
        
        system_prompt = prompt_manager.get_random("interview_questions").get("system_prompt", "")
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = await asyncio.to_thread(self._client.models.generate_content, model=MODEL, contents=full_prompt)
        
        logger.info("Gemini API call successful (branded as %s)", branded_provider)
        
        brand_map = {"openai": "openai", "gemini": "gemini", "claude": "claude"}
        
        return {
            "provider": brand_map.get(branded_provider.lower(), "gemini"),
            "questions": response.text,
            "usage": {}
        }
    
