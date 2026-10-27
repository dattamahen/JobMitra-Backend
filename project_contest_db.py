"""
Project Contest Database Operations.
All raw DB access for the contest feature lives here.
"""

import logging
import uuid
import re
from datetime import datetime, timedelta
from typing import Optional

from db import db
from project_contest_schemas import PRICING, LEVEL_WAIT_DAYS

logger = logging.getLogger(__name__)
COLLECTION = "project_contest_entries"
GMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@gmail\.com$')


class ProjectContestDB:

    @property
    def col(self):
        return db.database[COLLECTION]

    # ── Helpers ──────────────────────────────────────────────

    def generate_entry_id(self) -> str:
        """Generate unique PRJ-YYMMDD-XXXXXXXX id."""
        ts = datetime.utcnow().strftime("%y%m%d")
        return f"PRJ-{ts}-{uuid.uuid4().hex[:8].upper()}"

    def determine_pricing(self, team_size: int) -> tuple[str, float]:
        """Return (tier, amount) based on team size."""
        if team_size <= 1:
            return "solo", PRICING["solo"]
        return "team", PRICING["team"]

    def validate_gmail(self, email: str) -> bool:
        return bool(GMAIL_REGEX.match(email))

    def _serialize(self, doc: dict) -> dict:
        """Convert ObjectId and datetimes for JSON response."""
        doc.pop("_id", None)
        for key, val in doc.items():
            if isinstance(val, datetime):
                doc[key] = val.isoformat() + "Z"
        return doc

    # ── Create ───────────────────────────────────────────────

    async def create_entry(self, entry: dict) -> str:
        """Insert a new contest entry. Returns entry_id."""
        await self.col.insert_one(entry)
        return entry["entry_id"]

    # ── Read ─────────────────────────────────────────────────

    async def get_by_id(self, entry_id: str) -> Optional[dict]:
        """Fetch entry by entry_id."""
        doc = await self.col.find_one({"entry_id": entry_id}, {"_id": 0})
        return doc

    async def get_by_id_and_lead(self, entry_id: str, lead_user_id: str) -> Optional[dict]:
        """Fetch entry only if the requesting user is the lead."""
        return await self.col.find_one(
            {"entry_id": entry_id, "lead_user_id": lead_user_id}, {"_id": 0}
        )

    async def get_user_entries(self, user_id: str) -> list:
        """All entries where user is lead."""
        cursor = self.col.find({"lead_user_id": user_id}, {"_id": 0}).sort("created_at", -1)
        docs = await cursor.to_list(length=50)
        return [self._serialize(d) for d in docs]

    async def get_participant_entry(self, entry_id: str, user_id: str) -> Optional[dict]:
        """Fetch entry where user is lead OR a team member (for interview access)."""
        doc = await self.col.find_one({"entry_id": entry_id}, {"_id": 0})
        if not doc:
            return None
        if doc.get("lead_user_id") == user_id:
            return doc
        members = doc.get("team_members", [])
        if any(m.get("user_id") == user_id for m in members):
            return doc
        return None

    # ── Update helpers ───────────────────────────────────────

    async def set_fields(self, entry_id: str, fields: dict) -> None:
        """Generic $set update."""
        fields["updated_at"] = datetime.utcnow()
        await self.col.update_one({"entry_id": entry_id}, {"$set": fields})

    async def push_to_array(self, entry_id: str, field: str, value: dict) -> None:
        """Append item to an array field."""
        await self.col.update_one(
            {"entry_id": entry_id},
            {"$push": {field: value}, "$set": {"updated_at": datetime.utcnow()}}
        )

    # ── Level-specific updates ───────────────────────────────

    async def confirm_spark(self, entry_id: str, refined: dict) -> None:
        """Store LLM-refined idea and mark spark_confirmed."""
        await self.set_fields(entry_id, {
            "refined_title": refined.get("refined_title"),
            "refined_description": refined.get("refined_description"),
            "inferred_domain": refined.get("inferred_domain"),
            "inferred_problem_statement": refined.get("inferred_problem_statement"),
            "inferred_target_users": refined.get("inferred_target_users"),
            "idea_quality_score": refined.get("idea_quality_score", 0),
            "status": "spark_confirmed",
            "spark_confirmed_at": datetime.utcnow(),
            "blueprint_opens_at": datetime.utcnow() + timedelta(days=LEVEL_WAIT_DAYS["blueprint"]),
        })

    async def confirm_payment(self, entry_id: str, upi_id: str, amount: float, benefits: dict) -> None:
        """Mark payment confirmed and grant subscription."""
        await self.set_fields(entry_id, {
            "payment_status": "confirmed",
            "upi_transaction_id": upi_id,
            "amount_paid": amount,
            "subscription_granted": True,
            "subscription_benefits": benefits,
        })

    async def store_blueprint_questions(self, entry_id: str, questions: list) -> None:
        """Store LLM-generated questionnaire and open blueprint level."""
        await self.set_fields(entry_id, {
            "blueprint_questions": questions,
            "status": "blueprint_open",
        })

    async def submit_blueprint(self, entry_id: str, answers: list) -> None:
        """Store team's blueprint answers."""
        await self.set_fields(entry_id, {
            "blueprint_answers": answers,
            "status": "blueprint_submitted",
            "blueprint_submitted_at": datetime.utcnow(),
        })

    async def store_blueprint_evaluation(self, entry_id: str, result: dict, advance: bool) -> None:
        """Store blueprint evaluation result and set next status."""
        next_status = "blueprint_evaluated"
        fields = {
            "blueprint_score": result.get("blueprint_score", 0),
            "blueprint_dimension_scores": result.get("dimension_scores", {}),
            "blueprint_feedback": result.get("feedback_summary", ""),
            "blueprint_evaluated_at": datetime.utcnow(),
            "status": next_status,
        }
        if advance:
            fields["proof_opens_at"] = datetime.utcnow() + timedelta(days=LEVEL_WAIT_DAYS["proof"])
        else:
            fields["eliminated_at_level"] = "blueprint"
            fields["status"] = "eliminated"
        await self.set_fields(entry_id, fields)

    async def submit_proof(self, entry_id: str, youtube_url: str, github_url: str, demo_url: Optional[str]) -> None:
        """Store demo links."""
        await self.set_fields(entry_id, {
            "youtube_url": youtube_url,
            "github_url": github_url,
            "demo_url": demo_url,
            "status": "proof_submitted",
            "proof_submitted_at": datetime.utcnow(),
        })

    async def store_proof_evaluation(self, entry_id: str, result: dict, advance: bool) -> None:
        """Store demo evaluation result."""
        fields = {
            "demo_score": result.get("demo_score", 0),
            "demo_dimension_scores": result.get("dimension_scores", {}),
            "demo_red_flags": result.get("demo_red_flags", []),
            "demo_feedback": result.get("feedback_summary", ""),
            "proof_evaluated_at": datetime.utcnow(),
            "status": "proof_evaluated",
        }
        if advance:
            fields["interview_opens_at"] = datetime.utcnow() + timedelta(days=LEVEL_WAIT_DAYS["interview"])
        else:
            fields["eliminated_at_level"] = "proof"
            fields["status"] = "eliminated"
        await self.set_fields(entry_id, fields)

    async def init_interview_session(self, entry_id: str, participant_user_id: str,
                                     participant_role: str, round1_questions: list) -> None:
        """Create interview session for one participant."""
        session = {
            "participant_user_id": participant_user_id,
            "participant_role": participant_role,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat() + "Z",
            "rounds": [
                {
                    "round_number": 1,
                    "round_name": "Conceptual Depth",
                    "questions": round1_questions,
                    "answers": [],
                    "evaluations": [],
                    "round_score": None,
                    "consistency_rating": None,
                    "authenticity_assessment": None,
                    "knowledge_pattern": None,
                }
            ],
            "final_score": None,
            "overall_verdict": None,
            "participant_summary": None,
            "anomaly_flags": [],
            "feedback_for_participant": None,
        }
        await self.col.update_one(
            {"entry_id": entry_id},
            {
                "$push": {"interview_sessions": session},
                "$set": {"status": "interview_in_progress", "updated_at": datetime.utcnow()}
            }
        )

    async def store_answer_evaluation(self, entry_id: str, participant_user_id: str,
                                      round_number: int, question_id: int,
                                      answer: str, evaluation: dict) -> None:
        """Append answer + evaluation to the correct round of the participant's session."""
        answer_doc = {
            "question_id": question_id,
            "answer": answer,
            "submitted_at": datetime.utcnow().isoformat() + "Z",
        }
        eval_doc = {"question_id": question_id, **evaluation}

        await self.col.update_one(
            {
                "entry_id": entry_id,
                "interview_sessions.participant_user_id": participant_user_id,
                "interview_sessions.rounds.round_number": round_number,
            },
            {
                "$push": {
                    "interview_sessions.$[sess].rounds.$[rnd].answers": answer_doc,
                    "interview_sessions.$[sess].rounds.$[rnd].evaluations": eval_doc,
                },
                "$set": {"updated_at": datetime.utcnow()}
            },
            array_filters=[
                {"sess.participant_user_id": participant_user_id},
                {"rnd.round_number": round_number},
            ]
        )

    async def store_round_summary(self, entry_id: str, participant_user_id: str,
                                  round_number: int, summary: dict) -> None:
        """Store round-level summary scores."""
        await self.col.update_one(
            {
                "entry_id": entry_id,
                "interview_sessions.participant_user_id": participant_user_id,
                "interview_sessions.rounds.round_number": round_number,
            },
            {
                "$set": {
                    "interview_sessions.$[sess].rounds.$[rnd].round_score": summary.get("round_score"),
                    "interview_sessions.$[sess].rounds.$[rnd].consistency_rating": summary.get("consistency_rating"),
                    "interview_sessions.$[sess].rounds.$[rnd].authenticity_assessment": summary.get("authenticity_assessment"),
                    "interview_sessions.$[sess].rounds.$[rnd].knowledge_pattern": summary.get("knowledge_pattern"),
                    "updated_at": datetime.utcnow(),
                }
            },
            array_filters=[
                {"sess.participant_user_id": participant_user_id},
                {"rnd.round_number": round_number},
            ]
        )

    async def store_participant_final_score(self, entry_id: str, participant_user_id: str,
                                            result: dict) -> None:
        """Store final participant score after all 3 rounds."""
        await self.col.update_one(
            {"entry_id": entry_id, "interview_sessions.participant_user_id": participant_user_id},
            {
                "$set": {
                    "interview_sessions.$[sess].final_score": result.get("final_score"),
                    "interview_sessions.$[sess].overall_verdict": result.get("overall_verdict"),
                    "interview_sessions.$[sess].participant_summary": result.get("participant_summary"),
                    "interview_sessions.$[sess].anomaly_flags": result.get("anomaly_flags", []),
                    "interview_sessions.$[sess].feedback_for_participant": result.get("feedback_for_participant"),
                    "interview_sessions.$[sess].status": "complete",
                    "updated_at": datetime.utcnow(),
                }
            },
            array_filters=[{"sess.participant_user_id": participant_user_id}]
        )

    async def store_team_interview_result(self, entry_id: str, team_result: dict,
                                          composite_score: float, advance: bool) -> None:
        """Store team-level interview score and composite score."""
        fields = {
            "team_interview_score": team_result.get("team_interview_score"),
            "team_verdict": team_result.get("team_verdict"),
            "composite_score": composite_score,
            "interview_completed_at": datetime.utcnow(),
            "status": "interview_complete",
        }
        if advance:
            fields["status"] = "finalist"
        else:
            fields["status"] = "eliminated"
            fields["eliminated_at_level"] = "interview"
        await self.set_fields(entry_id, fields)

    async def declare_winner(self, entry_id: str) -> None:
        """Mark entry as winner."""
        await self.set_fields(entry_id, {
            "status": "winner",
            "winner_badge_granted": True,
            "winner_declared_at": datetime.utcnow(),
        })

    # ── Subscription ─────────────────────────────────────────

    async def grant_subscription(self, user_id: str, benefits: dict) -> None:
        """Add contest credits to a user."""
        await db.database["users"].update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "credits.cv_downloads_remaining": benefits["cv_downloads"],
                    "credits.mock_interviews_remaining": benefits["mock_interviews"],
                    "credits.total_cv_downloads": benefits["cv_downloads"],
                    "credits.total_mock_interviews": benefits["mock_interviews"],
                },
                "$set": {"user_plan": "paid", "updated_at": datetime.utcnow()},
            }
        )

    async def grant_subscription_by_email(self, email: str, benefits: dict) -> bool:
        """Grant subscription to a team member by email. Returns True if user found."""
        user = await db.database["users"].find_one({"email": email})
        if user:
            await self.grant_subscription(user["user_id"], benefits)
            return True
        return False


contest_db = ProjectContestDB()
