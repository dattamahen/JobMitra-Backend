"""
FastAPI main application for JobMitra Backend.
Provides REST API endpoints for query processing with AI agents.
"""

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import our custom modules
from crew_agent import run_crew_ai, run_resume_enhancement_crew
from db import db, log_to_db
from api_routes import router as api_router


# Load environment variables from .env file
load_dotenv()


# Pydantic models for request and response validation
class QueryRequest(BaseModel):
    """Request model for the /ask endpoint."""
    query: str
    
    class Config:
        # Example for API documentation
        schema_extra = {
            "example": {
                "query": "What are the best practices for Python web development?"
            }
        }


class ResumeEnhanceRequest(BaseModel):
    """Request model for the /resume-enhance endpoint."""
    resume: str
    job_description: str
    
    class Config:
        # Example for API documentation
        schema_extra = {
            "example": {
                "resume": "John Doe\nSoftware Developer\n...",
                "job_description": "We are looking for a Senior Full Stack Developer..."
            }
        }


class QueryResponse(BaseModel):
    """Response model for the /ask endpoint."""
    response: str
    timestamp: datetime = None
    
    class Config:
        # Example for API documentation
        schema_extra = {
            "example": {
                "response": "Here are the best practices for Python web development...",
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class ResumeEnhanceResponse(BaseModel):
    """Response model for the /resume-enhance endpoint."""
    enhanced_resume: str
    timestamp: datetime = None
    
    class Config:
        # Example for API documentation
        schema_extra = {
            "example": {
                "enhanced_resume": "Enhanced resume content with improvements...",
                "timestamp": "2024-01-15T10:30:00"
            }
        }


# Async context manager for application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup: Initialize database connection
    print("Starting JobMitra Backend API...")
    
    try:
        await db.connect_to_mongo()
        print("Database connection established successfully")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        # You might want to exit here in production
        
    yield
    
    # Shutdown: Close database connection
    print("Shutting down JobMitra Backend API...")
    await db.close_mongo_connection()


# Initialize FastAPI application with metadata
app = FastAPI(
    title="JobMitra Backend API",
    description="""
    A comprehensive REST API for JobMitra that processes user queries using AI agents powered by CrewAI.
    
    Features:
    - AI-powered query processing
    - User profile management
    - Job search and application tracking
    - Mock interview system
    - Learning resources and progress tracking
    - Dashboard analytics
    - MongoDB integration for data persistence
    - OpenAI integration via CrewAI
    """,
    version="2.0.0",
    lifespan=lifespan
)

# Include additional API routes
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint for health checking.
    
    Returns:
        dict: API status and information
    """
    return {
        "message": "JobMitra Backend API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }


# Main query processing endpoint
@app.post("/ask", response_model=QueryResponse, tags=["Query Processing"])
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
        
        # Process query using CrewAI
        print("Processing query with AI agents...")
        ai_response = run_crew_ai(user_query)
        
        if not ai_response:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate AI response"
            )
        
        # Log interaction to database (non-blocking)
        print("Logging interaction to database...")
        try:
            await log_to_db(user_query, ai_response)
        except Exception as db_error:
            # Log database error but don't fail the request
            print(f"Database logging failed: {db_error}")
        
        # Return successful response
        response = QueryResponse(
            response=ai_response,
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


# Resume enhancement endpoint
@app.post("/resume-enhance", response_model=ResumeEnhanceResponse, tags=["Resume Enhancement"])
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
        
        # Process resume enhancement using CrewAI 3-agent workflow
        print("Processing resume enhancement with AI agents...")
        enhanced_resume = run_resume_enhancement_crew(resume_content, job_desc_content)
        
        if not enhanced_resume:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate enhanced resume"
            )
        
        # Log resume enhancement to database (non-blocking)
        print("Logging resume enhancement to database...")
        try:
            # Create a log entry for resume enhancement
            resume_log_data = {
                "original_resume": resume_content,
                "job_description": job_desc_content,
                "enhanced_resume": enhanced_resume,
                "timestamp": datetime.utcnow(),
                "process_type": "resume_enhancement"
            }
            
            # Log to resume_logs collection
            collection = db.database["resume_logs"]
            await collection.insert_one(resume_log_data)
            
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


# Additional endpoint to get recent query logs (optional)
@app.get("/logs", tags=["Logs"])
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
            
        # Import here to avoid circular imports
        from db import get_query_logs
        
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


# Resume logs endpoint
@app.get("/resume-logs", tags=["Logs"])
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
        
        # Get resume logs from database
        collection = db.database["resume_logs"]
        cursor = collection.find().sort("timestamp", -1).limit(limit)
        resume_logs = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for log in resume_logs:
            log["_id"] = str(log["_id"])
        
        return {
            "resume_logs": resume_logs,
            "count": len(resume_logs),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        print(f"Error retrieving resume logs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve resume logs"
        )


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    # Check if required environment variables are set
    required_env_vars = ["OPENAI_API_KEY", "MONGO_URI"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {missing_vars}")
        print("Please check your .env file")
    
    # Start the server
    print("Starting JobMitra Backend API server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
