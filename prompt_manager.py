"""
Prompt Manager — Loads prompt variants from JSON files and provides
random selection with per-user repeat avoidance.
"""

import json
import os
import random
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"

# Valid category names mapped to filenames
CATEGORIES = {
    "interview_questions": "interview_questions.json",
    "interview_evaluation": "interview_evaluation.json",
    "resume_tailoring": "resume_tailoring.json",
    "resume_validation": "resume_validation.json",
    "resume_enhancement": "resume_enhancement.json",
    "query_analysis": "query_analysis.json",
}


class PromptManager:
    """Manages prompt variants with random selection and repeat avoidance."""

    def __init__(self):
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._user_history: Dict[str, Dict[str, List[str]]] = {}
        self._load_all()

    # ── Loading ──────────────────────────────────────────────

    def _load_all(self):
        for category, filename in CATEGORIES.items():
            filepath = PROMPTS_DIR / filename
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._cache[category] = data.get("variants", [])
                    logger.info(
                        "Loaded %d variants for '%s'",
                        len(self._cache[category]),
                        category,
                    )
                except Exception as e:
                    logger.error("Failed to load %s: %s", filepath, e)
                    self._cache[category] = []
            else:
                logger.warning("Prompt file not found: %s", filepath)
                self._cache[category] = []

    def reload(self):
        """Hot-reload all prompt files without restart."""
        self._cache.clear()
        self._load_all()
        logger.info("Prompts reloaded")

    # ── Selection ────────────────────────────────────────────

    def get_random(
        self,
        category: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Return a random prompt variant for *category*.

        If *user_id* is provided the selector avoids recently used variants
        for that user (cycles through all before repeating).
        """
        variants = self._cache.get(category, [])
        if not variants:
            logger.warning("No variants for category '%s', returning fallback", category)
            return self._fallback(category)

        if user_id:
            return self._pick_avoiding_repeats(category, variants, user_id)

        return random.choice(variants)

    def get_by_id(self, category: str, variant_id: str) -> Optional[Dict[str, Any]]:
        """Return a specific variant by its id."""
        for v in self._cache.get(category, []):
            if v.get("id") == variant_id:
                return v
        return None

    def get_by_style(self, category: str, style: str) -> Optional[Dict[str, Any]]:
        """Return a specific variant by its style tag."""
        for v in self._cache.get(category, []):
            if v.get("style") == style:
                return v
        return None

    def list_variants(self, category: str) -> List[Dict[str, str]]:
        """Return summary list of available variants for a category."""
        return [
            {"id": v["id"], "name": v["name"], "style": v.get("style", "")}
            for v in self._cache.get(category, [])
        ]

    def list_categories(self) -> List[str]:
        """Return all available prompt categories."""
        return list(self._cache.keys())

    # ── Repeat avoidance ─────────────────────────────────────

    def _pick_avoiding_repeats(
        self,
        category: str,
        variants: List[Dict[str, Any]],
        user_id: str,
    ) -> Dict[str, Any]:
        if user_id not in self._user_history:
            self._user_history[user_id] = {}

        used = self._user_history[user_id].get(category, [])
        all_ids = [v["id"] for v in variants]

        # Reset history when all variants have been used
        unused_ids = [vid for vid in all_ids if vid not in used]
        if not unused_ids:
            self._user_history[user_id][category] = []
            unused_ids = all_ids

        chosen_id = random.choice(unused_ids)
        self._user_history[user_id].setdefault(category, []).append(chosen_id)

        return next(v for v in variants if v["id"] == chosen_id)

    def clear_user_history(self, user_id: str, category: Optional[str] = None):
        """Reset repeat-avoidance history for a user."""
        if user_id in self._user_history:
            if category:
                self._user_history[user_id].pop(category, None)
            else:
                del self._user_history[user_id]

    # ── Fallbacks ────────────────────────────────────────────

    @staticmethod
    def _fallback(category: str) -> Dict[str, Any]:
        fallbacks = {
            "interview_questions": {
                "id": "fallback",
                "name": "Default Interviewer",
                "system_prompt": "You are an expert interviewer. Generate specific interview questions based on the given prompt. Format as numbered list.",
                "style": "default",
                "temperature": 0.7,
            },
            "interview_evaluation": {
                "id": "fallback",
                "name": "Default Evaluator",
                "system_prompt": "You are an expert technical interviewer. Evaluate this interview performance and provide a detailed assessment.",
                "style": "default",
                "temperature": 0.5,
            },
            "resume_tailoring": {
                "id": "fallback",
                "name": "Default Resume Writer",
                "system_prompt": "You are an expert resume writer and hiring manager. Tailor the resume for the job description while preserving truthfulness.",
                "style": "default",
                "temperature": 0.7,
            },
            "resume_validation": {
                "id": "fallback",
                "name": "Default Resume Validator",
                "system_prompt": "You are an expert HR professional and ATS specialist. Compare the resume with the job description and provide a match analysis.",
                "style": "default",
                "temperature": 0.5,
            },
            "resume_enhancement": {
                "id": "fallback",
                "name": "Default Enhancement Advisor",
                "system_prompt": "You are a professional resume writer. Suggest improvements to the resume based on best practices.",
                "style": "default",
                "temperature": 0.7,
            },
            "query_analysis": {
                "id": "fallback",
                "name": "Default Researcher",
                "system_prompt": "You are an expert researcher. Analyze and answer user queries with accurate, comprehensive information.",
                "style": "default",
                "temperature": 0.7,
            },
        }
        return fallbacks.get(
            category,
            {"id": "fallback", "system_prompt": "You are a helpful AI assistant.", "style": "default", "temperature": 0.7},
        )


# ── Singleton ────────────────────────────────────────────────
prompt_manager = PromptManager()
