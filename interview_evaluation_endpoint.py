from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from multi_llm_service import MultiLLMService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
llm_service = MultiLLMService()

class QuestionAnswer(BaseModel):
    question_id: str
    question: str
    answer: str

class InterviewSubmission(BaseModel):
    session_id: str
    user_profile: Dict[str, Any]
    questions_and_answers: List[QuestionAnswer]

@router.post("/submit-for-evaluation")
async def submit_interview_for_evaluation(submission: InterviewSubmission):
    """Submit interview for LLM evaluation"""
    try:
        # Prepare evaluation prompt
        user_info = f"Role: {submission.user_profile.get('role', 'N/A')}\n"
        user_info += f"Experience: {submission.user_profile.get('experience_years', 0)} years\n"
        user_info += f"Skills: {', '.join(submission.user_profile.get('skills', []))}\n\n"
        
        qa_text = ""
        for i, qa in enumerate(submission.questions_and_answers, 1):
            qa_text += f"Question {i}: {qa.question}\n"
            qa_text += f"Answer {i}: {qa.answer}\n\n"
        
        evaluation_prompt = f"""Evaluate this interview performance:

{user_info}Interview Questions and Answers:
{qa_text}

Provide evaluation in this JSON format:
{{
    "overall_score": 85,
    "feedback": "Overall performance summary...",
    "question_scores": [
        {{"question_id": "q_1", "score": 80, "feedback": "Good understanding but could improve..."}},
        {{"question_id": "q_2", "score": 90, "feedback": "Excellent answer with clear examples..."}}
    ]
}}

Evaluate based on technical accuracy, communication clarity, and depth of understanding."""

        # Get evaluation from LLM
        ai_response = await llm_service.generate(evaluation_prompt, "gemini")
        
        return {
            "success": True,
            "session_id": submission.session_id,
            "evaluation_submitted": True,
            "message": "Interview submitted for evaluation successfully"
        }
        
    except Exception as e:
        logger.error(f"Error submitting interview for evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit interview: {str(e)}")

@router.get("/evaluation/{session_id}")
async def get_interview_evaluation(session_id: str):
    """Get interview evaluation results"""
    try:
        # This would typically fetch from database
        # For now, return a mock evaluation
        return {
            "session_id": session_id,
            "overall_score": 85,
            "feedback": "Good overall performance with room for improvement in system design concepts.",
            "question_scores": [
                {"question_id": "q_1", "score": 80, "feedback": "Good understanding of basic concepts"},
                {"question_id": "q_2", "score": 90, "feedback": "Excellent practical knowledge"}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation: {str(e)}")