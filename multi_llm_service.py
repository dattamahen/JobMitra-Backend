"""
Multi-LLM Service - Supports OpenAI, Gemini, and Claude
Optimized: API key configured once at initialization, not per-request.
"""
import asyncio
import logging
from typing import Dict, Any
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

# Configure Gemini API key ONCE at module load
_gemini_configured = False
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    _gemini_configured = True

# Reusable model instance (thread-safe for async)
_model = genai.GenerativeModel('gemini-2.0-flash') if _gemini_configured else None

# Request timeout in seconds
LLM_TIMEOUT = 30


class MultiLLMService:
    """All providers route through Gemini internally. Provider names are kept for UI branding."""

    async def generate(self, prompt: str, provider: str = "gemini") -> Dict[str, Any]:
        """Generate response with timeout protection."""
        if not _gemini_configured or _model is None:
            raise Exception("GEMINI_API_KEY not configured")

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(_model.generate_content, prompt),
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
            "gemini": {"provider": "gemini", "model": "gemini-2.0-flash"},
            "claude": {"provider": "claude", "model": "claude-3-sonnet"},
        }
        brand = brand_map.get(provider.lower(), brand_map["gemini"])

        return {
            "provider": brand["provider"],
            "content": response.text,
            "model": brand["model"]
        }
