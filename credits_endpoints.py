"""
Credits and Payment endpoints for JobMitra Backend.
Credits are stored as a subdocument inside the users collection.
Payment audit log is kept in a separate payments collection.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import db
from activity_tracker import log_user_activity

router = APIRouter(tags=["Credits & Payments"])

# Constants
FREE_CV_DOWNLOADS = 3
FREE_MOCK_INTERVIEWS = 2
PAID_CV_DOWNLOADS = 10
PAID_MOCK_INTERVIEWS = 10
PAID_AMOUNT = 149  # INR including GST
MAX_PAYMENT_HISTORY = 50

PAYMENTS_COLLECTION = "payments"


# Request/Response Models
class PaymentConfirmRequest(BaseModel):
    user_id: str
    upi_transaction_id: str
    amount: float = PAID_AMOUNT


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
        defaults = {
            "cv_downloads_remaining": FREE_CV_DOWNLOADS,
            "mock_interviews_remaining": FREE_MOCK_INTERVIEWS,
            "total_cv_downloads": FREE_CV_DOWNLOADS,
            "total_mock_interviews": FREE_MOCK_INTERVIEWS,
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


@router.post("/api/v1/payments/confirm")
async def confirm_payment(req: PaymentConfirmRequest):
    """User confirms UPI payment. Credits are added immediately (trust-based)."""
    try:
        if req.amount != PAID_AMOUNT:
            raise HTTPException(status_code=400, detail=f"Amount must be ₹{PAID_AMOUNT}")

        # Ensure user exists and has credits initialised
        await _get_credits(req.user_id)

        users = db.database["users"]

        payment_record = {
            "upi_transaction_id": req.upi_transaction_id,
            "amount": req.amount,
            "currency": "INR",
            "status": "confirmed",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Atomic update: increment credits + push payment + update plan
        await users.update_one(
            {"user_id": req.user_id},
            {
                "$inc": {
                    "credits.cv_downloads_remaining": PAID_CV_DOWNLOADS,
                    "credits.mock_interviews_remaining": PAID_MOCK_INTERVIEWS,
                    "credits.total_cv_downloads": PAID_CV_DOWNLOADS,
                    "credits.total_mock_interviews": PAID_MOCK_INTERVIEWS,
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
