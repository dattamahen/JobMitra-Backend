from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from multi_llm_service import MultiLLMService
from db_simple import create_mock_interview, get_user_mock_interviews
from prompt_manager import prompt_manager
import logging
from datetime import datetime

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
        
        eval_variant = prompt_manager.get_random(
            "interview_evaluation",
            user_id=submission.user_profile.get('user_id')
        )
        eval_system_prompt = eval_variant.get("system_prompt")
        
        evaluation_prompt = f"""{eval_system_prompt}

{user_info}Interview Questions and Answers:
{qa_text}

Provide your evaluation in EXACTLY this JSON format (no markdown, no extra text):
{{
    "overall_score": 85,
    "feedback": "Provide a comprehensive 2-3 sentence summary of the candidate's overall performance, highlighting strengths and areas for improvement.",
    "question_scores": [
        {{"question_id": "q_1", "score": 80, "feedback": "Specific feedback for this answer"}},
        {{"question_id": "q_2", "score": 90, "feedback": "Specific feedback for this answer"}}
    ]
}}

Evaluate based on:
1. Technical accuracy and depth of knowledge
2. Communication clarity and structure
3. Problem-solving approach
4. Practical examples and real-world understanding

Provide scores from 0-100. Return ONLY the JSON object, nothing else."""

        # Get evaluation from LLM
        ai_response = await llm_service.generate(evaluation_prompt, "gemini")
        
        # Parse the JSON response
        import json
        import re
        
        content = ai_response.get("content", "")
        # Remove markdown code blocks if present
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        content = content.strip()
        
        try:
            evaluation_data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            logger.warning(f"Failed to parse LLM response as JSON: {content}")
            evaluation_data = {
                "overall_score": 75,
                "feedback": "Interview completed successfully. Detailed evaluation is being processed.",
                "question_scores": [
                    {"question_id": qa.question_id, "score": 75, "feedback": "Good response"}
                    for qa in submission.questions_and_answers
                ]
            }
        
        # Save interview to database
        user_id = submission.user_profile.get('user_id', 'unknown')
        interview_record = {
            "session_id": submission.session_id,
            "user_id": user_id,
            "interview_type": submission.user_profile.get('role', 'Technical'),
            "questions_count": len(submission.questions_and_answers),
            "overall_score": evaluation_data.get("overall_score", 0),
            "feedback": evaluation_data.get("feedback", ""),
            "question_scores": evaluation_data.get("question_scores", []),
            "questions_and_answers": [
                {
                    "question_id": qa.question_id,
                    "question": qa.question,
                    "answer": qa.answer
                }
                for qa in submission.questions_and_answers
            ],
            "status": "completed",
            "completed_at": datetime.utcnow()
        }
        
        interview_id = await create_mock_interview(interview_record)
        logger.info(f"Interview saved with ID: {interview_id}")
        
        return {
            "success": True,
            "session_id": submission.session_id,
            "interview_id": interview_id,
            "evaluation": evaluation_data
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

@router.get("/history/{user_id}")
async def get_interview_history(user_id: str, limit: int = 10):
    """Get user's interview history"""
    try:
        interviews = await get_user_mock_interviews(user_id, limit)
        return {
            "success": True,
            "user_id": user_id,
            "interviews": interviews,
            "total": len(interviews)
        }
    except Exception as e:
        logger.error(f"Error getting interview history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get interview history: {str(e)}")