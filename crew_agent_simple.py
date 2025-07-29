"""
Mock agent module for development/testing purposes.
Provides sample responses without external AI dependencies.
"""

import os
from typing import Dict, Any


def run_crew_ai(query: str) -> Dict[str, Any]:
    """
    Mock query processing that returns sample responses.
    
    Args:
        query (str): User query to process
        
    Returns:
        Dict[str, Any]: Response with answer and metadata
    """
    # Sample responses based on common career queries
    sample_responses = {
        "interview": "Here are some key interview tips: 1) Research the company thoroughly, 2) Practice common interview questions, 3) Prepare specific examples using the STAR method, 4) Dress appropriately, 5) Ask thoughtful questions about the role and company culture.",
        "resume": "For an effective resume: 1) Use a clean, professional format, 2) Tailor your resume to each job application, 3) Quantify your achievements with numbers, 4) Include relevant keywords from the job description, 5) Keep it concise (1-2 pages).",
        "career": "Career development tips: 1) Set clear short and long-term goals, 2) Continuously learn new skills, 3) Build a professional network, 4) Seek feedback and mentorship, 5) Stay updated with industry trends.",
        "skills": "To develop in-demand skills: 1) Identify skills gaps in your field, 2) Take online courses or certifications, 3) Work on practical projects, 4) Join professional communities, 5) Practice regularly and seek feedback."
    }
    
    # Find the most relevant response
    query_lower = query.lower()
    response_key = "career"  # default
    
    for key in sample_responses.keys():
        if key in query_lower:
            response_key = key
            break
    
    return {
        "answer": f"Based on your query about '{query}', here's my advice: {sample_responses[response_key]}",
        "metadata": {
            "status": "success",
            "mode": "mock_response",
            "query_type": response_key
        }
    }


def run_resume_enhancement_crew(resume: str, job_description: str) -> Dict[str, Any]:
    """
    Mock resume enhancement that returns sample improvements.
    
    Args:
        resume (str): Original resume content
        job_description (str): Target job description
        
    Returns:
        Dict[str, Any]: Enhanced resume and suggestions
    """
    enhanced_resume = f"""
ENHANCED RESUME (Sample Enhancement):

{resume}

--- IMPROVEMENTS MADE ---
• Added relevant keywords from the job description
• Strengthened action verbs and quantified achievements
• Improved formatting and structure
• Highlighted skills that match the job requirements

Note: This is a mock enhancement. For real AI-powered improvements, configure your OpenAI API key.
"""
    
    suggestions = [
        "Tailor your resume specifically to this job posting",
        "Quantify your achievements with specific numbers and percentages",
        "Use strong action verbs to describe your responsibilities",
        "Include relevant keywords from the job description",
        "Ensure your contact information is up-to-date",
        "Proofread for grammar and spelling errors"
    ]
    
    return {
        "enhanced_resume": enhanced_resume,
        "suggestions": suggestions,
        "metadata": {
            "status": "success",
            "mode": "mock_enhancement",
            "original_length": len(resume),
            "enhanced_length": len(enhanced_resume)
        }
    }
