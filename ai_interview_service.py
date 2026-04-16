import logging
logger = logging.getLogger(__name__)

import requests
import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logger.debug("Loading .env file...")
logger.debug("OpenAI API Key loaded: %s", bool(os.getenv('OPENAI_API_KEY')))
from config import settings
from prompt_manager import prompt_manager

class AIInterviewService:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    async def generate_interview_questions(self, prompt_template: str, ai_provider: str = 'openai') -> Dict[str, Any]:
        """Generate interview questions using AI"""
        try:
            if ai_provider.lower() == 'openai':
                return await self._generate_with_openai(prompt_template)

            else:
                raise ValueError(f"Unsupported AI provider: {ai_provider}")
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")
    
    async def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Generate questions using OpenAI GPT via HTTP requests"""
        if not self.openai_api_key:
            raise Exception("OpenAI API key not found")
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": prompt_manager.get_random("interview_questions").get("system_prompt")},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
        )
        
        logger.debug("OpenAI API Response Status: %s", response.status_code)
        if response.status_code != 200:
            logger.debug("OpenAI API Error Response: %s", response.text)
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
        
        logger.info("OpenAI API call successful!")
        
        result = response.json()
        
        return {
            "provider": "openai",
            "questions": result['choices'][0]['message']['content'],
            "usage": result.get('usage', {})
        }
    
