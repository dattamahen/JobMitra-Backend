"""
Seed subscription_plans collection into MongoDB.
Run: py seed_subscription_plans.py
"""

import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

PLANS = [
    # ── Free tier (same across all envs) ──
    {
        "plan_id": "free_tier",
        "name": "Free Tier",
        "description": "Get started with limited credits",
        "amount": 0,
        "currency": "INR",
        "cv_downloads": 3,
        "mock_interviews": 2,
        "is_active": True,
        "is_default": True,
        "env": "all",
        "upi_id": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    # ── Paid plan for local (₹1 for testing on localhost:4200) ──
    {
        "plan_id": "pro_test_local",
        "name": "Pro Plan (Test)",
        "description": "Test plan — ₹1 for local development",
        "amount": 2,
        "currency": "INR",
        "cv_downloads": 10,
        "mock_interviews": 10,
        "is_active": True,
        "is_default": False,
        "env": "local",
        "upi_id": "jobmouka@upi",
        "payment_link": "https://razorpay.me/@sanchamtechnologysolutionspri?amount=2",
        "benefits": [
            {"icon": "record_voice_over", "text": "10 AI Mock Interviews", "detail": "practice until you're confident"},
            {"icon": "description", "text": "10 CV Downloads", "detail": "apply to more companies, faster"},
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    # ── Paid plan for dev (₹1 for testing on dev.jobmouka.com) ──
    {
        "plan_id": "pro_149_dev",
        "name": "Pro Plan",
        "description": "Unlock 10 CV downloads and 10 mock interviews",
        "amount": 2,
        "currency": "INR",
        "cv_downloads": 10,
        "mock_interviews": 10,
        "is_active": True,
        "is_default": False,
        "env": "dev",
        "upi_id": "jobmouka@upi",
        "payment_link": "https://razorpay.me/@sanchamtechnologysolutionspri?amount=2",
        "benefits": [
            {"icon": "record_voice_over", "text": "10 AI Mock Interviews", "detail": "practice until you're confident"},
            {"icon": "description", "text": "10 CV Downloads", "detail": "apply to more companies, faster"},
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    # ── Paid plan for prod (₹149 on www.jobmouka.com) ──
    {
        "plan_id": "pro_149_prod",
        "name": "Pro Plan",
        "description": "Unlock 10 CV downloads and 10 mock interviews",
        "amount": 149,
        "currency": "INR",
        "cv_downloads": 10,
        "mock_interviews": 10,
        "is_active": True,
        "is_default": False,
        "env": "prod",
        "upi_id": "jobmouka@upi",
        "payment_link": "https://razorpay.me/@sanchamtechnologysolutionspri?amount=149",
        "benefits": [
            {"icon": "record_voice_over", "text": "10 AI Mock Interviews", "detail": "practice until you're confident"},
            {"icon": "description", "text": "10 CV Downloads", "detail": "apply to more companies, faster"},
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]


async def seed():
    uri = os.getenv("MONGO_URI")
    client = AsyncIOMotorClient(uri)
    db_name = uri.split("/")[-1].split("?")[0]
    db = client[db_name]
    collection = db["subscription_plans"]

    # Drop existing plans and re-seed
    await collection.delete_many({})
    result = await collection.insert_many(PLANS)
    print(f"Inserted {len(result.inserted_ids)} subscription plans:")
    for plan in PLANS:
        print(f"  - {plan['plan_id']}: {plan['name']} (Rs.{plan['amount']})")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
