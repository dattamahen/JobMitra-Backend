"""
Multi-LLM Service - Supports OpenAI, Gemini, and Claude
"""
import os
from typing import Dict, Any
from openai import OpenAI
import google.generativeai as genai
from anthropic import Anthropic

class MultiLLMService:
	def __init__(self):
		self.openai_key = os.getenv("OPENAI_API_KEY")
		self.gemini_key = os.getenv("GEMINI_API_KEY")
		self.claude_key = os.getenv("ANTHROPIC_API_KEY")
	
	async def generate(self, prompt: str, provider: str = "openai") -> Dict[str, Any]:
		"""Generate response using specified LLM provider"""
		provider = provider.lower()
		
		if provider == "openai":
			return await self._generate_openai(prompt)
		elif provider == "gemini":
			return await self._generate_gemini(prompt)
		elif provider == "claude":
			return await self._generate_claude(prompt)
		else:
			raise ValueError(f"Unsupported provider: {provider}")
	
	async def _generate_openai(self, prompt: str) -> Dict[str, Any]:
		"""Generate using OpenAI GPT-3.5-turbo"""
		if not self.openai_key:
			raise Exception("OPENAI_API_KEY not configured")
		
		client = OpenAI(api_key=self.openai_key)
		response = client.chat.completions.create(
			model="gpt-3.5-turbo",
			messages=[{"role": "user", "content": prompt}],
			temperature=0.7
		)
		
		return {
			"provider": "openai",
			"content": response.choices[0].message.content,
			"model": "gpt-3.5-turbo"
		}
	
	async def _generate_gemini(self, prompt: str) -> Dict[str, Any]:
		"""Generate using Google Gemini"""
		if not self.gemini_key:
			raise Exception("GEMINI_API_KEY not configured")
		
		genai.configure(api_key=self.gemini_key)
		model = genai.GenerativeModel('gemini-2.5-flash')
		response = model.generate_content(prompt)
		
		return {
			"provider": "gemini",
			"content": response.text,
			"model": "gemini-2.5-flash"
		}
	
	async def _generate_claude(self, prompt: str) -> Dict[str, Any]:
		"""Generate using Anthropic Claude"""
		if not self.claude_key:
			raise Exception("ANTHROPIC_API_KEY not configured")
		
		client = Anthropic(api_key=self.claude_key)
		response = client.messages.create(
			model="claude-3-sonnet-20240229",
			max_tokens=1024,
			messages=[{"role": "user", "content": prompt}]
		)
		
		return {
			"provider": "claude",
			"content": response.content[0].text,
			"model": "claude-3-sonnet"
		}
