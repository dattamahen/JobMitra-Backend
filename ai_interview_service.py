import requests
import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print(f"Loading .env file...")
print(f"OpenAI API Key loaded: {bool(os.getenv('OPENAI_API_KEY'))}")
from config import settings

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
                {"role": "system", "content": "You are an expert interviewer. Generate 5-10 specific interview questions based on the given prompt. Format as numbered list."},
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
        
        print(f"OpenAI API Response Status: {response.status_code}")
        if response.status_code != 200:
            print(f"OpenAI API Error Response: {response.text}")
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
        
        print("OpenAI API call successful!")
        
        result = response.json()
        
        return {
            "provider": "openai",
            "questions": result['choices'][0]['message']['content'],
            "usage": result.get('usage', {})
        }
    
