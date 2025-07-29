"""
FastAPI main application for JobMitra Backend.
Provides REST API endpoints for query processing with AI agents.
"""

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import our custom modules
from crew_agent_simple import run_crew_ai, run_resume_enhancement_crew
from db_simple import db, log_to_db  # Simplified MongoDB database
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular default port
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:4200",  # Alternative localhost format
        "http://127.0.0.1:3000",  # Alternative localhost format
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Include additional API routes
app.include_router(api_router, prefix="/api/v1")

# Simple dashboard endpoint for testing CORS
@app.get("/api/v1/dashboard", tags=["Dashboard"])
async def get_dashboard():
    """Dashboard endpoint that returns data compatible with Angular frontend."""
    from datetime import datetime
    
    return {
        "stats": [
            {
                "id": "applications",
                "label": "Applications Sent",
                "value": 12,
                "icon": "send",
                "color": "primary",
                "trend": {
                    "direction": "up",
                    "percentage": 15,
                    "period": "this week"
                }
            },
            {
                "id": "interviews",
                "label": "Interviews Scheduled", 
                "value": 3,
                "icon": "event",
                "color": "accent",
                "trend": {
                    "direction": "up",
                    "percentage": 50,
                    "period": "this week"
                }
            },
            {
                "id": "total-jobs",
                "label": "Total Jobs Available",
                "value": 150,
                "icon": "work",
                "color": "info",
                "trend": {
                    "direction": "neutral",
                    "percentage": 0,
                    "period": "this week"
                }
            },
            {
                "id": "profile-completion",
                "label": "Profile Completion",
                "value": "85%",
                "icon": "account_circle",
                "color": "success",
                "trend": {
                    "direction": "up",
                    "percentage": 10,
                    "period": "this week"
                }
            }
        ],
        "recentActivities": [
            {
                "id": "1",
                "title": "Applied to Software Engineer position at TechCorp",
                "icon": "send",
                "timestamp": datetime.now().isoformat(),
                "type": "application",
                "status": "pending"
            },
            {
                "id": "2", 
                "title": "Completed mock interview for Backend Developer role",
                "icon": "quiz",
                "timestamp": datetime.now().isoformat(),
                "type": "interview",
                "status": "completed"
            },
            {
                "id": "3",
                "title": "Updated resume with new skills",
                "icon": "description",
                "timestamp": datetime.now().isoformat(), 
                "type": "resume",
                "status": "completed"
            }
        ],
        "lastUpdated": datetime.now().isoformat()
    }

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
        "version": "2.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "cors_enabled": True
    }


# CORS test endpoint
@app.get("/cors-test", tags=["Health"])
async def cors_test():
    """
    Simple endpoint to test CORS configuration.
    """
    return {
        "message": "CORS is working!",
        "timestamp": datetime.utcnow(),
        "access_from": "Angular frontend should be able to access this"
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
