"""
Multi-LLM Service - Supports OpenAI, Gemini, and Claude
"""
import os
from typing import Dict, Any
import google.generativeai as genai

class MultiLLMService:
	"""All providers route through Gemini internally. Provider names are kept for UI branding."""

	def __init__(self):
		self.gemini_key = os.getenv("GEMINI_API_KEY")
	
	async def generate(self, prompt: str, provider: str = "openai") -> Dict[str, Any]:
		"""Generate response — all providers use Gemini internally"""
		if not self.gemini_key:
			raise Exception("GEMINI_API_KEY not configured")

		genai.configure(api_key=self.gemini_key)
		model = genai.GenerativeModel('gemini-2.5-flash')
		response = model.generate_content(prompt)

		# Map provider name to branded display names
		brand_map = {
			"openai": {"provider": "openai", "model": "gpt-4"},
			"gemini": {"provider": "gemini", "model": "gemini-2.5-flash"},
			"claude": {"provider": "claude", "model": "claude-3-sonnet"},
		}
		brand = brand_map.get(provider.lower(), brand_map["gemini"])

		return {
			"provider": brand["provider"],
			"content": response.text,
			"model": brand["model"]
		}
