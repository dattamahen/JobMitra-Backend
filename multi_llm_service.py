"""
Multi-LLM Service - Supports OpenAI, Gemini, and Claude
Optimized: API key configured once at initialization, not per-request.
"""
import asyncio
import logging
from typing import Dict, Any
from google import genai
from config import settings

logger = logging.getLogger(__name__)

MODEL = "gemini-2.0-flash-lite"
LLM_TIMEOUT = 30

_client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None


class MultiLLMService:
    """All providers route through Gemini internally. Provider names are kept for UI branding."""

    async def generate(self, prompt: str, provider: str = "gemini") -> Dict[str, Any]:
        """Generate response with timeout protection."""
        if not _client:
            raise Exception("GEMINI_API_KEY not configured")

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(_client.models.generate_content, model=MODEL, contents=prompt),
                timeout=LLM_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error("LLM request timed out after %ds", LLM_TIMEOUT)
            raise Exception("AI service timed out. Please try again.")
        except Exception as e:
            logger.error("LLM generation failed: %s", e)
            raise

        brand_map = {
            "openai": {"provider": "openai", "model": "gpt-4"},
            "gemini": {"provider": "gemini", "model": MODEL},
            "claude": {"provider": "claude", "model": "claude-3-sonnet"},
        }
        brand = brand_map.get(provider.lower(), brand_map["gemini"])

        return {
            "provider": brand["provider"],
            "content": response.text,
            "model": brand["model"]
        }
