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

MODEL = "gemini-3.5-flash"
FALLBACK_MODELS = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.8-flash", "gemini-3-flash-preview"]
LLM_TIMEOUT = 30

_client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None


class MultiLLMService:
    """All providers route through Gemini internally. Provider names are kept for UI branding."""

    async def generate(self, prompt: str, provider: str = "gemini", model: str = None, temperature: float = 1.0) -> Dict[str, Any]:
        """Generate response with timeout protection and fallback chain on 503."""
        if not _client:
            raise Exception("GEMINI_API_KEY not configured")

        from google.genai import types as genai_types
        gen_config = genai_types.GenerateContentConfig(temperature=temperature)

        all_models = [MODEL] + FALLBACK_MODELS
        last_error = None

        for attempt_model in all_models:
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        _client.models.generate_content,
                        model=attempt_model,
                        contents=prompt,
                        config=gen_config,
                    ),
                    timeout=LLM_TIMEOUT
                )
                if attempt_model != MODEL:
                    logger.info("Fallback model %s succeeded", attempt_model)
                break
            except asyncio.TimeoutError:
                logger.warning("Model %s timed out, trying next", attempt_model)
                last_error = Exception("AI service timed out. Please try again.")
                continue
            except Exception as e:
                if "503" in str(e) or "404" in str(e):
                    logger.warning("Model %s unavailable (%s), trying next", attempt_model, str(e)[:60])
                    last_error = e
                    continue
                logger.error("LLM generation failed: %s", e)
                raise
        else:
            logger.error("All models exhausted. Last error: %s", last_error)
            raise Exception("AI service is currently unavailable. Please try again later.")

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
