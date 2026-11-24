"""
Admin endpoints for the engagement email campaign system.
All endpoints require authentication and admin role (email == ADMIN_EMAIL).
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from auth_endpoints import get_current_user
from engagement_email_db import engagement_email_db
from engagement_email_schemas import CampaignConfigUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/engagement", tags=["Engagement Campaigns"])

_ADMIN_EMAIL = "renukadevi@jobmouka.com"


def _require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency — raises 403 if the caller is not the admin."""
    if current_user.get("email") != _ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/campaigns")
async def list_campaigns(current_user: dict = Depends(_require_admin)):
    """List all engagement campaign configurations."""
    configs = await engagement_email_db.get_all_configs()
    return {"success": True, "data": configs, "message": f"{len(configs)} campaigns"}


@router.put("/campaigns/{campaign_id}")
async def update_campaign(
    campaign_id: str,
    body: CampaignConfigUpdate,
    current_user: dict = Depends(_require_admin),
):
    """Update a campaign config (enabled flag, thresholds, schedule)."""
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=422, detail="No fields provided to update")
    found = await engagement_email_db.update_config(campaign_id, updates)
    if not found:
        raise HTTPException(status_code=404, detail="Campaign not found")
    config = await engagement_email_db.get_config(campaign_id)
    return {"success": True, "data": config, "message": "Campaign updated"}


@router.post("/campaigns/{campaign_id}/run", status_code=202)
async def trigger_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(_require_admin),
):
    """Manually trigger a campaign run in the background."""
    config = await engagement_email_db.get_config(campaign_id)
    if not config:
        raise HTTPException(status_code=404, detail="Campaign not found")

    from engagement_email_runner import run_campaign
    background_tasks.add_task(run_campaign, campaign_id, config)
    logger.info("Manual campaign trigger: %s by %s", campaign_id, current_user.get("user_id"))
    return {"success": True, "data": None, "message": f"Campaign '{campaign_id}' queued"}


@router.get("/logs")
async def get_send_logs(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(_require_admin),
):
    """Return paginated engagement email send history."""
    if per_page > 100:
        per_page = 100
    result = await engagement_email_db.get_logs(page=page, per_page=per_page)
    return {"success": True, "data": result, "message": "Send log retrieved"}
