"""
Pydantic models for request and response validation.
"""

from datetime import datetime
from pydantic import BaseModel


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
