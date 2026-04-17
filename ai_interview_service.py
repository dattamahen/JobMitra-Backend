import logging
logger = logging.getLogger(__name__)

import json
from typing import Dict, Any
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
from config import settings
from prompt_manager import prompt_manager

class AIInterviewService:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    async def generate_interview_questions(self, prompt_template: str, ai_provider: str = 'openai') -> Dict[str, Any]:
        """Generate interview questions using Gemini (all providers route through Gemini)"""
        try:
            return await self._generate_with_gemini(prompt_template, ai_provider)
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")
    
    async def _generate_with_gemini(self, prompt: str, branded_provider: str = 'openai') -> Dict[str, Any]:
        """Generate questions using Gemini internally"""
        if not self.gemini_api_key:
            raise Exception("GEMINI_API_KEY not found")
        
        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = prompt_manager.get_random("interview_questions").get("system_prompt", "")
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(full_prompt)
        )
        
        logger.info("Gemini API call successful (branded as %s)", branded_provider)
        
        # Brand the response with the requested provider name
        brand_map = {
            "openai": "openai",
            "gemini": "gemini",
            "claude": "claude",
        }
        
        return {
            "provider": brand_map.get(branded_provider.lower(), "gemini"),
            "questions": response.text,
            "usage": {}
        }
    
