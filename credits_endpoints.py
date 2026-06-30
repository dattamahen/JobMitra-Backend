"""
Credits and Payment endpoints for JobMitra Backend.
Credits are stored as a subdocument inside the users collection.
Payment audit log is kept in a separate payments collection.
Plan configuration is read from the subscription_plans collection.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import db
from config import settings
from activity_tracker import log_user_activity

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Credits & Payments"])

# Fallback constants (used only if DB lookup fails)
_FALLBACK_FREE = {"cv_downloads": 3, "mock_interviews": 2, "amount": 0}
_FALLBACK_PAID = {"cv_downloads": 10, "mock_interviews": 10, "amount": 149, "upi_id": "jobmouka@upi"}

MAX_PAYMENT_HISTORY = 50
PAYMENTS_COLLECTION = "payments"
PLANS_COLLECTION = "subscription_plans"


# ── Plan helpers ─────────────────────────────────────────────

async def _get_plan(plan_id: str = None, *, is_default: bool = False) -> dict:
    """Fetch a plan from subscription_plans collection, filtered by current APP_ENV."""
    try:
        collection = db.database[PLANS_COLLECTION]
        query = {"is_active": True}
        if plan_id:
            query["plan_id"] = plan_id
        if is_default:
            query["is_default"] = True
        else:
            # Non-default (paid) plans are env-specific
            query["env"] = {"$in": [settings.APP_ENV, "all"]}
        plan = await collection.find_one(query, {"_id": 0})
        return plan
    except Exception as e:
        logger.warning("Failed to fetch plan from DB: %s", e)
        return None


async def _get_free_plan() -> dict:
    plan = await _get_plan(is_default=True)
    return plan or _FALLBACK_FREE


async def _get_paid_plan() -> dict:
    """Get the active paid plan for the current environment."""
    try:
        collection = db.database[PLANS_COLLECTION]
        plan = await collection.find_one(
            {
                "is_active": True,
                "is_default": False,
                "amount": {"$gt": 0},
                "env": settings.APP_ENV,
            },
            {"_id": 0}
        )
        return plan or _FALLBACK_PAID
    except Exception as e:
        logger.warning("Failed to fetch paid plan from DB: %s", e)
        return _FALLBACK_PAID


# Request/Response Models
class PaymentConfirmRequest(BaseModel):
    user_id: str
    upi_transaction_id: str
    amount: float


class DeductCreditRequest(BaseModel):
    user_id: str
    credit_type: str  # "cv_download" or "mock_interview"


# ── Helpers ──────────────────────────────────────────────────

async def _get_credits(user_id: str) -> dict:
    """
    Read credits from users.credits subdocument.
    Initialises defaults if the field is missing (first-time user).
    """
    users = db.database["users"]
    user = await users.find_one({"user_id": user_id}, {"credits": 1})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "credits" not in user or not user["credits"]:
        free_plan = await _get_free_plan()
        defaults = {
            "cv_downloads_remaining": free_plan.get("cv_downloads", 3),
            "mock_interviews_remaining": free_plan.get("mock_interviews", 2),
            "total_cv_downloads": free_plan.get("cv_downloads", 3),
            "total_mock_interviews": free_plan.get("mock_interviews", 2),
            "total_paid": 0,
            "payment_history": [],
        }
        await users.update_one(
            {"user_id": user_id},
            {"$set": {"credits": defaults}},
        )
        return defaults

    return user["credits"]


# ── Endpoints ────────────────────────────────────────────────

@router.get("/api/v1/users/{user_id}/credits")
async def get_user_credits(user_id: str):
    """Get remaining credits for a user."""
    try:
        credits = await _get_credits(user_id)
        return {
            "user_id": user_id,
            "cv_downloads_remaining": credits.get("cv_downloads_remaining", 0),
            "mock_interviews_remaining": credits.get("mock_interviews_remaining", 0),
            "total_paid": credits.get("total_paid", 0),
            "is_paid_user": credits.get("total_paid", 0) > 0,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/subscription-plan")
async def get_active_subscription_plan():
    """Return the active paid subscription plan details (amount, credits, payment link)."""
    plan = await _get_paid_plan()
    return {
        "plan_id": plan.get("plan_id", "pro_149"),
        "name": plan.get("name", "Pro Plan"),
        "description": plan.get("description", ""),
        "amount": plan.get("amount", 149),
        "currency": plan.get("currency", "INR"),
        "cv_downloads": plan.get("cv_downloads", 10),
        "mock_interviews": plan.get("mock_interviews", 10),
        "upi_id": plan.get("upi_id", "jobmouka@upi"),
        "payment_link": plan.get("payment_link", ""),
        "benefits": plan.get("benefits", []),
    }


@router.post("/api/v1/payments/confirm")
async def confirm_payment(req: PaymentConfirmRequest):
    """User confirms UPI payment. Credits are added immediately (trust-based)."""
    try:
        paid_plan = await _get_paid_plan()
        expected_amount = paid_plan.get("amount", 149)

        if req.amount != expected_amount:
            raise HTTPException(status_code=400, detail=f"Amount must be ₹{expected_amount}")

        # Ensure user exists and has credits initialised
        await _get_credits(req.user_id)

        users = db.database["users"]
        cv_credits = paid_plan.get("cv_downloads", 10)
        interview_credits = paid_plan.get("mock_interviews", 10)

        payment_record = {
            "upi_transaction_id": req.upi_transaction_id,
            "amount": req.amount,
            "currency": paid_plan.get("currency", "INR"),
            "plan_id": paid_plan.get("plan_id", "pro_149"),
            "status": "confirmed",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Atomic update: increment credits + push payment + update plan
        await users.update_one(
            {"user_id": req.user_id},
            {
                "$inc": {
                    "credits.cv_downloads_remaining": cv_credits,
                    "credits.mock_interviews_remaining": interview_credits,
                    "credits.total_cv_downloads": cv_credits,
                    "credits.total_mock_interviews": interview_credits,
                    "credits.total_paid": req.amount,
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

        # Audit log in separate collection (append-only financial ledger)
        await db.database[PAYMENTS_COLLECTION].insert_one({
            "user_id": req.user_id,
            **payment_record,
        })

        # Read back updated credits
        updated = await _get_credits(req.user_id)

        # Track activity
        await log_user_activity(
            req.user_id,
            "subscription",
            f"Purchased premium plan — ₹{int(req.amount)}",
            {"upi_transaction_id": req.upi_transaction_id, "amount": req.amount},
        )

        return {
            "message": "Payment confirmed. Credits added successfully.",
            "cv_downloads_remaining": updated.get("cv_downloads_remaining", 0),
            "mock_interviews_remaining": updated.get("mock_interviews_remaining", 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/credits/deduct")
async def deduct_credit(req: DeductCreditRequest):
    """Deduct a credit before allowing a paid feature."""
    try:
        credits = await _get_credits(req.user_id)
        users = db.database["users"]

        if req.credit_type == "cv_download":
            if credits.get("cv_downloads_remaining", 0) <= 0:
                raise HTTPException(
                    status_code=403,
                    detail="No CV download credits remaining. Please purchase more.",
                )
            await users.update_one(
                {"user_id": req.user_id},
                {
                    "$inc": {"credits.cv_downloads_remaining": -1},
                    "$set": {"updated_at": datetime.utcnow()},
                },
            )
            await log_user_activity(req.user_id, "cv_download", "Downloaded resume as PDF")

        elif req.credit_type == "mock_interview":
            if credits.get("mock_interviews_remaining", 0) <= 0:
                raise HTTPException(
                    status_code=403,
                    detail="No mock interview credits remaining. Please purchase more.",
                )
            await users.update_one(
                {"user_id": req.user_id},
                {
                    "$inc": {"credits.mock_interviews_remaining": -1},
                    "$set": {"updated_at": datetime.utcnow()},
                },
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid credit_type. Use 'cv_download' or 'mock_interview'.",
            )

        updated = await _get_credits(req.user_id)
        return {
            "message": f"{req.credit_type} credit deducted.",
            "cv_downloads_remaining": updated.get("cv_downloads_remaining", 0),
            "mock_interviews_remaining": updated.get("mock_interviews_remaining", 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/users/{user_id}/payment-history")
async def get_payment_history(user_id: str):
    """Get payment history for a user."""
    try:
        credits = await _get_credits(user_id)
        return {
            "user_id": user_id,
            "payments": credits.get("payment_history", []),
            "total_paid": credits.get("total_paid", 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
