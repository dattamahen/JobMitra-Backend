"""
Core API endpoints for JobMitra Backend.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException

from models import QueryRequest, QueryResponse, ResumeEnhanceRequest, ResumeEnhanceResponse
from crew_agent_simple import run_crew_ai, run_resume_enhancement_crew
from db_simple import log_to_db


# Create router for core endpoints
router = APIRouter()


@router.post("/ask", response_model=QueryResponse, tags=["Query Processing"])
async def ask_question(request: QueryRequest):
    """
    Process user queries using AI agents and return intelligent responses.
    
    This endpoint:
    1. Receives a user query
    2. Processes it using CrewAI agents
    3. Logs the interaction to MongoDB
    4. Returns the AI-generated response
    
    Args:
        request (QueryRequest): JSON payload containing the user query
        
    Returns:
        QueryResponse: AI-generated response with timestamp
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        # Validate input
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=400, 
                detail="Query cannot be empty"
            )
        
        user_query = request.query.strip()
        print(f"Received query: {user_query}")
        
        # Process query using AI agents
        print("Processing query with AI agents...")
        ai_response = run_crew_ai(user_query)
        
        if not ai_response or not ai_response.get("answer"):
            raise HTTPException(
                status_code=500,
                detail="Failed to generate AI response"
            )
        
        # Extract the answer from the AI response
        answer = ai_response.get("answer", "No response generated")
        
        # Log interaction to database (non-blocking)
        print("Logging interaction to database...")
        try:
            await log_to_db(user_query, answer, ai_response.get("metadata", {}))
        except Exception as db_error:
            # Log database error but don't fail the request
            print(f"Database logging failed: {db_error}")
        
        # Return successful response
        response = QueryResponse(
            response=answer,
            timestamp=datetime.utcnow()
        )
        
        print("Query processed successfully")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Unexpected error in /ask endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/resume-enhance", response_model=ResumeEnhanceResponse, tags=["Resume Enhancement"])
async def enhance_resume(request: ResumeEnhanceRequest):
    """
    Enhance a resume based on a job description using AI agents.
    
    This endpoint:
    1. Receives a resume and job description
    2. Processes them using a 3-agent CrewAI workflow:
       - Agent 1: Analyzes resume vs job description match
       - Agent 2: Suggests improvements based on analysis
       - Agent 3: Generates enhanced resume
    3. Logs the enhancement process to MongoDB
    4. Returns the enhanced resume
    
    Args:
        request (ResumeEnhanceRequest): JSON payload containing resume and job description
        
    Returns:
        ResumeEnhanceResponse: Enhanced resume with timestamp
        
    Raises:
        HTTPException: If resume enhancement fails
    """
    try:
        # Validate input
        if not request.resume or not request.resume.strip():
            raise HTTPException(
                status_code=400, 
                detail="Resume content cannot be empty"
            )
        
        if not request.job_description or not request.job_description.strip():
            raise HTTPException(
                status_code=400, 
                detail="Job description cannot be empty"
            )
        
        resume_content = request.resume.strip()
        job_desc_content = request.job_description.strip()
        
        print(f"Received resume enhancement request")
        print(f"Resume length: {len(resume_content)} characters")
        print(f"Job description length: {len(job_desc_content)} characters")
        
        # Process resume enhancement using AI agents
        print("Processing resume enhancement with AI agents...")
        enhancement_result = run_resume_enhancement_crew(resume_content, job_desc_content)
        
        if not enhancement_result or not enhancement_result.get("enhanced_resume"):
            raise HTTPException(
                status_code=500,
                detail="Failed to generate enhanced resume"
            )
        
        enhanced_resume = enhancement_result.get("enhanced_resume", "Enhancement failed")
        
        # Log resume enhancement to database (non-blocking)
        print("Logging resume enhancement to database...")
        try:
            # Use the mock database logging function
            await log_to_db(
                f"Resume Enhancement Request", 
                enhanced_resume,
                {
                    "original_resume_length": len(resume_content),
                    "job_description_length": len(job_desc_content),
                    "process_type": "resume_enhancement"
                }
            )
            
        except Exception as db_error:
            # Log database error but don't fail the request
            print(f"Database logging failed: {db_error}")
        
        # Return successful response
        response = ResumeEnhanceResponse(
            enhanced_resume=enhanced_resume,
            timestamp=datetime.utcnow()
        )
        
        print("Resume enhancement processed successfully")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Unexpected error in /resume-enhance endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/logs", tags=["Logs"])
async def get_recent_logs(limit: int = 10):
    """
    Retrieve recent query logs from the database.
    
    Args:
        limit (int): Number of recent logs to retrieve (default: 10, max: 100)
        
    Returns:
        dict: List of recent query logs
    """
    try:
        # Validate limit parameter
        if limit > 100:
            limit = 100
        elif limit < 1:
            limit = 10
            
        # Import the function from db_simple
        from db_simple import get_query_logs
        logs = await get_query_logs(limit)
        
        return {
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve logs"
        )


@router.get("/resume-logs", tags=["Logs"])
async def get_recent_resume_logs(limit: int = 10):
    """
    Retrieve recent resume enhancement logs from the database.
    
    Args:
        limit (int): Number of recent resume logs to retrieve (default: 10, max: 50)
        
    Returns:
        dict: List of recent resume enhancement logs
    """
    try:
        # Validate limit parameter
        if limit > 50:
            limit = 50
        elif limit < 1:
            limit = 10
        
        # Get all logs and filter for resume enhancement
        from db_simple import get_query_logs
        all_logs = await get_query_logs(100)  # Get more logs to filter
        
        resume_logs = [log for log in all_logs if 
                      log.get("metadata", {}).get("process_type") == "resume_enhancement"]
        
        return {
            "resume_logs": resume_logs[-limit:],
            "count": len(resume_logs[-limit:]),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        print(f"Error retrieving resume logs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve resume logs"
        )
