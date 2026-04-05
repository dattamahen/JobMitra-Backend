"""
Credits and Payment endpoints for JobMitra Backend.
Handles user credits (CV downloads, mock interviews) and UPI payment flow.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db_simple import db

router = APIRouter(tags=["Credits & Payments"])

# Constants
FREE_CV_DOWNLOADS = 3
FREE_MOCK_INTERVIEWS = 2
PAID_CV_DOWNLOADS = 10
PAID_MOCK_INTERVIEWS = 10
PAID_AMOUNT = 149  # INR including GST

COLLECTION = "user_credits"
PAYMENTS_COLLECTION = "payments"


# Request/Response Models
class PaymentConfirmRequest(BaseModel):
    user_id: str
    upi_transaction_id: str
    amount: float = PAID_AMOUNT


class DeductCreditRequest(BaseModel):
    user_id: str
    credit_type: str  # "cv_download" or "mock_interview"


# Helper: ensure credits doc exists
async def _ensure_credits(user_id: str) -> dict:
    collection = db.database[COLLECTION]
    credits = await collection.find_one({"user_id": user_id})
    if not credits:
        credits = {
            "user_id": user_id,
            "cv_downloads_remaining": FREE_CV_DOWNLOADS,
            "mock_interviews_remaining": FREE_MOCK_INTERVIEWS,
            "total_cv_downloads": FREE_CV_DOWNLOADS,
            "total_mock_interviews": FREE_MOCK_INTERVIEWS,
            "total_paid": 0,
            "payment_history": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await collection.insert_one(credits)
        credits = await collection.find_one({"user_id": user_id})
    if "_id" in credits:
        credits["_id"] = str(credits["_id"])
    return credits


@router.get("/api/v1/users/{user_id}/credits")
async def get_user_credits(user_id: str):
    """Get remaining credits for a user."""
    try:
        credits = await _ensure_credits(user_id)
        return {
            "user_id": user_id,
            "cv_downloads_remaining": credits.get("cv_downloads_remaining", 0),
            "mock_interviews_remaining": credits.get("mock_interviews_remaining", 0),
            "total_paid": credits.get("total_paid", 0),
            "is_paid_user": credits.get("total_paid", 0) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/payments/confirm")
async def confirm_payment(req: PaymentConfirmRequest):
    """User confirms UPI payment. Credits are added immediately (trust-based)."""
    try:
        if req.amount != PAID_AMOUNT:
            raise HTTPException(status_code=400, detail=f"Amount must be ₹{PAID_AMOUNT}")

        credits = await _ensure_credits(req.user_id)
        collection = db.database[COLLECTION]

        payment_record = {
            "upi_transaction_id": req.upi_transaction_id,
            "amount": req.amount,
            "currency": "INR",
            "status": "confirmed",
            "timestamp": datetime.utcnow()
        }

        # Add credits and record payment
        await collection.update_one(
            {"user_id": req.user_id},
            {
                "$inc": {
                    "cv_downloads_remaining": PAID_CV_DOWNLOADS,
                    "mock_interviews_remaining": PAID_MOCK_INTERVIEWS,
                    "total_cv_downloads": PAID_CV_DOWNLOADS,
                    "total_mock_interviews": PAID_MOCK_INTERVIEWS,
                    "total_paid": req.amount
                },
                "$push": {"payment_history": payment_record},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        # Also store in payments collection for audit
        await db.database[PAYMENTS_COLLECTION].insert_one({
            "user_id": req.user_id,
            **payment_record
        })

        # Update user plan in users collection
        users_collection = db.database["users"]
        await users_collection.update_one(
            {"user_id": req.user_id},
            {"$set": {"user_plan": "paid", "updated_at": datetime.utcnow()}}
        )

        updated = await _ensure_credits(req.user_id)
        return {
            "message": "Payment confirmed. Credits added successfully.",
            "cv_downloads_remaining": updated.get("cv_downloads_remaining", 0),
            "mock_interviews_remaining": updated.get("mock_interviews_remaining", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/credits/deduct")
async def deduct_credit(req: DeductCreditRequest):
    """Deduct a credit before allowing a paid feature."""
    try:
        credits = await _ensure_credits(req.user_id)
        collection = db.database[COLLECTION]

        if req.credit_type == "cv_download":
            if credits.get("cv_downloads_remaining", 0) <= 0:
                raise HTTPException(status_code=403, detail="No CV download credits remaining. Please purchase more.")
            await collection.update_one(
                {"user_id": req.user_id},
                {"$inc": {"cv_downloads_remaining": -1}, "$set": {"updated_at": datetime.utcnow()}}
            )
        elif req.credit_type == "mock_interview":
            if credits.get("mock_interviews_remaining", 0) <= 0:
                raise HTTPException(status_code=403, detail="No mock interview credits remaining. Please purchase more.")
            await collection.update_one(
                {"user_id": req.user_id},
                {"$inc": {"mock_interviews_remaining": -1}, "$set": {"updated_at": datetime.utcnow()}}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid credit_type. Use 'cv_download' or 'mock_interview'.")

        updated = await _ensure_credits(req.user_id)
        return {
            "message": f"{req.credit_type} credit deducted.",
            "cv_downloads_remaining": updated.get("cv_downloads_remaining", 0),
            "mock_interviews_remaining": updated.get("mock_interviews_remaining", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/users/{user_id}/payment-history")
async def get_payment_history(user_id: str):
    """Get payment history for a user."""
    try:
        credits = await _ensure_credits(user_id)
        return {
            "user_id": user_id,
            "payments": credits.get("payment_history", []),
            "total_paid": credits.get("total_paid", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
