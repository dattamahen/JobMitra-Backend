from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

class InterviewQuestion(BaseModel):
    id: str
    question: str
    type: str  # "technical", "behavioral", "company-specific"

class StartInterviewRequest(BaseModel):
    interview_type: str  # "technical", "behavioral", "company-specific"
    difficulty: Optional[str] = "medium"
    company: Optional[str] = None

class InterviewSession(BaseModel):
    session_id: str
    questions: List[InterviewQuestion]
    created_at: datetime

class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str

class EvaluateInterviewRequest(BaseModel):
    session_id: str
    answers: List[dict]  # [{"question_id": "1", "answer": "text"}]

class InterviewEvaluation(BaseModel):
    session_id: str
    overall_score: int
    feedback: str
    question_scores: List[dict]

# Dummy questions database
DUMMY_QUESTIONS = {
    "technical": [
        {"id": "tech_1", "question": "Explain the difference between let, const, and var in JavaScript.", "type": "technical"},
        {"id": "tech_2", "question": "What is the time complexity of binary search?", "type": "technical"},
        {"id": "tech_3", "question": "How does React's virtual DOM work?", "type": "technical"},
        {"id": "tech_4", "question": "Explain the concept of closures in JavaScript.", "type": "technical"},
        {"id": "tech_5", "question": "What are the SOLID principles in software engineering?", "type": "technical"}
    ],
    "behavioral": [
        {"id": "beh_1", "question": "Tell me about a time when you had to work with a difficult team member.", "type": "behavioral"},
        {"id": "beh_2", "question": "Describe a situation where you had to learn a new technology quickly.", "type": "behavioral"},
        {"id": "beh_3", "question": "How do you handle tight deadlines and pressure?", "type": "behavioral"},
        {"id": "beh_4", "question": "Tell me about a project you're most proud of.", "type": "behavioral"},
        {"id": "beh_5", "question": "Describe a time when you had to give constructive feedback to a colleague.", "type": "behavioral"}
    ],
    "company-specific": [
        {"id": "comp_1", "question": "Why do you want to work at this company?", "type": "company-specific"},
        {"id": "comp_2", "question": "How would you contribute to our company culture?", "type": "company-specific"},
        {"id": "comp_3", "question": "What do you know about our products and services?", "type": "company-specific"},
        {"id": "comp_4", "question": "How do you align with our company values?", "type": "company-specific"},
        {"id": "comp_5", "question": "Where do you see yourself in 5 years with our company?", "type": "company-specific"}
    ]
}

# In-memory storage for sessions
interview_sessions = {}

@router.post("/api/v1/mock-interview/start", response_model=InterviewSession)
async def start_interview(request: StartInterviewRequest):
    """Start a new mock interview session"""
    try:
        session_id = str(uuid.uuid4())
        
        # Get questions based on type
        questions_data = DUMMY_QUESTIONS.get(request.interview_type, DUMMY_QUESTIONS["technical"])
        questions = [InterviewQuestion(**q) for q in questions_data]
        
        session = InterviewSession(
            session_id=session_id,
            questions=questions,
            created_at=datetime.now()
        )
        
        # Store session
        interview_sessions[session_id] = {
            "session": session,
            "answers": {}
        }
        
        return session
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")

@router.post("/api/v1/mock-interview/submit-answer")
async def submit_answer(request: SubmitAnswerRequest):
    """Submit answer for a specific question"""
    try:
        if request.session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        # Store the answer
        interview_sessions[request.session_id]["answers"][request.question_id] = request.answer
        
        return {"message": "Answer submitted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting answer: {str(e)}")

@router.post("/api/v1/mock-interview/evaluate", response_model=InterviewEvaluation)
async def evaluate_interview(request: EvaluateInterviewRequest):
    """Evaluate the complete interview"""
    try:
        if request.session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        session_data = interview_sessions[request.session_id]
        
        # Simple dummy evaluation logic
        total_questions = len(request.answers)
        answered_questions = len([a for a in request.answers if a.get("answer", "").strip()])
        
        # Calculate score based on completion and answer length
        completion_score = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
        
        question_scores = []
        for answer_data in request.answers:
            answer_text = answer_data.get("answer", "").strip()
            # Simple scoring: longer answers get higher scores
            score = min(100, len(answer_text.split()) * 10) if answer_text else 0
            question_scores.append({
                "question_id": answer_data.get("question_id"),
                "score": score,
                "feedback": "Good answer!" if score > 50 else "Could be more detailed."
            })
        
        overall_score = int(sum(q["score"] for q in question_scores) / len(question_scores)) if question_scores else 0
        
        feedback = f"You completed {answered_questions}/{total_questions} questions. "
        if overall_score >= 80:
            feedback += "Excellent performance! Your answers were comprehensive and well-structured."
        elif overall_score >= 60:
            feedback += "Good job! Consider providing more detailed examples in your answers."
        else:
            feedback += "Keep practicing! Try to provide more specific examples and details."
        
        evaluation = InterviewEvaluation(
            session_id=request.session_id,
            overall_score=overall_score,
            feedback=feedback,
            question_scores=question_scores
        )
        
        return evaluation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating interview: {str(e)}")