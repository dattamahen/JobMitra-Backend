"""
Prompt Management API Endpoints
"""

from fastapi import APIRouter, HTTPException
from prompt_manager import prompt_manager
from typing import Optional

router = APIRouter(prefix="/api/v1/prompts", tags=["Prompt Management"])


@router.get("/categories")
async def get_categories():
    """List all prompt categories."""
    return {"categories": prompt_manager.list_categories()}


@router.get("/{category}/variants")
async def get_variants(category: str):
    """List available variants for a category."""
    variants = prompt_manager.list_variants(category)
    if not variants:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    return {"category": category, "count": len(variants), "variants": variants}


@router.get("/{category}/random")
async def get_random_prompt(category: str, user_id: Optional[str] = None):
    """Get a random prompt variant (with optional user-level repeat avoidance)."""
    variant = prompt_manager.get_random(category, user_id)
    return {"category": category, "selected": variant}


@router.post("/reload")
async def reload_prompts():
    """Hot-reload all prompt files without server restart."""
    prompt_manager.reload()
    return {"message": "Prompts reloaded", "categories": prompt_manager.list_categories()}


@router.delete("/history/{user_id}")
async def clear_user_history(user_id: str, category: Optional[str] = None):
    """Clear repeat-avoidance history for a user."""
    prompt_manager.clear_user_history(user_id, category)
    return {"message": f"History cleared for user '{user_id}'"}
