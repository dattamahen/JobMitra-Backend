"""
Razorpay Payment Links integration for JobMitra.
Creates payment links with fixed amounts and handles webhooks.
"""
import hmac
import hashlib
import logging
import httpx
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from db import db
from config import settings
from activity_tracker import log_user_activity
from credits_endpoints import _get_credits, _get_paid_plan, MAX_PAYMENT_HISTORY, PAYMENTS_COLLECTION

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Payments"])


class CreatePaymentLinkRequest(BaseModel):
    user_id: str


async def _razorpay_request(method: str, path: str, payload: dict = None) -> dict:
    """Make authenticated request to Razorpay API."""
    url = f"https://api.razorpay.com/v1{path}"
    auth = (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, json=payload, auth=auth, timeout=10)
        if resp.status_code >= 400:
            logger.error("Razorpay API error %s: %s", resp.status_code, resp.text)
            raise HTTPException(status_code=502, detail="Payment service error")
        return resp.json()


@router.post("/api/v1/payments/create-link")
async def create_payment_link(req: CreatePaymentLinkRequest):
    """Create a Razorpay Payment Link with fixed amount for the user."""
    try:
        plan = await _get_paid_plan()
        amount_paise = int(plan.get("amount", 149)) * 100  # Razorpay uses paise

        # Get user info for prefill
        user = await db.database["users"].find_one(
            {"user_id": req.user_id},
            {"email": 1, "first_name": 1, "last_name": 1, "phone": 1}
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        payload = {
            "amount": amount_paise,
            "currency": "INR",
            "accept_partial": False,
            "description": plan.get("description", "JobMouka Pro Plan"),
            "customer": {
                "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                "email": user.get("email", ""),
                "contact": user.get("phone", ""),
            },
            "notify": {"sms": False, "email": True},
            "reminder_enable": False,
            "notes": {
                "user_id": req.user_id,
                "plan_id": plan.get("plan_id", ""),
                "env": settings.APP_ENV,
            },
            "callback_url": f"{settings.FRONTEND_URL}/subscription?payment=success",
            "callback_method": "get",
        }

        link = await _razorpay_request("POST", "/payment_links", payload)

        # Store pending payment record
        await db.database[PAYMENTS_COLLECTION].insert_one({
            "user_id": req.user_id,
            "payment_link_id": link["id"],
            "amount": plan.get("amount", 149),
            "currency": "INR",
            "plan_id": plan.get("plan_id", ""),
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

        return {
            "payment_link_id": link["id"],
            "payment_url": link["short_url"],
            "amount": plan.get("amount", 149),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating payment link: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create payment link")


@router.post("/payments/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None)
):
    """Handle Razorpay webhook for payment_link.paid event."""
    body = await request.body()

    # Verify signature
    expected = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, x_razorpay_signature or ""):
        logger.warning("Invalid Razorpay webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    import json
    event = json.loads(body)

    if event.get("event") != "payment_link.paid":
        return {"status": "ignored"}

    try:
        payload = event["payload"]["payment_link"]["entity"]
        payment_entity = event["payload"]["payment"]["entity"]

        user_id = payload.get("notes", {}).get("user_id")
        plan_id = payload.get("notes", {}).get("plan_id")
        amount_paid = payment_entity.get("amount", 0) / 100  # convert paise to INR
        payment_id = payment_entity.get("id")
        link_id = payload.get("id")

        if not user_id:
            logger.error("Webhook missing user_id in notes")
            return {"status": "error", "detail": "missing user_id"}

        # Get plan credits
        plan = await _get_paid_plan()
        cv_credits = plan.get("cv_downloads", 10)
        interview_credits = plan.get("mock_interviews", 10)

        payment_record = {
            "razorpay_payment_id": payment_id,
            "razorpay_link_id": link_id,
            "amount": amount_paid,
            "currency": "INR",
            "plan_id": plan_id or plan.get("plan_id", ""),
            "status": "paid",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Add credits atomically
        await db.database["users"].update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "credits.cv_downloads_remaining": cv_credits,
                    "credits.mock_interviews_remaining": interview_credits,
                    "credits.total_cv_downloads": cv_credits,
                    "credits.total_mock_interviews": interview_credits,
                    "credits.total_paid": amount_paid,
                },
                "$push": {
                    "credits.payment_history": {
                        "$each": [payment_record],
                        "$slice": -MAX_PAYMENT_HISTORY,
                    }
                },
                "$set": {
                    "user_plan": "paid",
                    "updated_at": datetime.utcnow(),
                },
            },
        )

        # Update payment record status
        await db.database[PAYMENTS_COLLECTION].update_one(
            {"payment_link_id": link_id},
            {"$set": {"status": "paid", "razorpay_payment_id": payment_id}}
        )

        await log_user_activity(
            user_id,
            "subscription",
            f"Payment successful — ₹{int(amount_paid)}",
            {"razorpay_payment_id": payment_id, "amount": amount_paid},
        )

        logger.info("Credits added for user %s via Razorpay payment %s", user_id, payment_id)
        return {"status": "ok"}

    except Exception as e:
        logger.error("Webhook processing error: %s", e)
        return {"status": "error", "detail": str(e)}
