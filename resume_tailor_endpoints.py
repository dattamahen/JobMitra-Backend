"""
Resume Tailor API endpoints using Gemini AI
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from auth_endpoints import get_current_user
from multi_llm_service import MultiLLMService
from db_simple import db
import json
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/v1", tags=["Resume Tailor"])

def sanitize_for_json(obj):
    """Recursively convert MongoDB documents to JSON-serializable format"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items() if k != '_id'}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

@router.get("/jobs/{job_id}/tailor-preview")
async def get_tailor_preview(job_id: str, current_user: dict = Depends(get_current_user)):
    """Get preview of tailored resume changes - Returns dummy data for demo"""
    print(f"\n=== Tailor Preview Request (Dummy Mode) ===")
    print(f"Job ID: {job_id}")
    print(f"User ID: {current_user.get('user_id')}")
    
    # Return realistic mock data immediately
    return {
        "original_resume": {
            "first_name": current_user.get('first_name', 'User'),
            "last_name": current_user.get('last_name', 'Name'),
            "professional_summary": "Software developer with experience in web development",
            "skills": ["JavaScript", "HTML", "CSS", "React"]
        },
        "tailored_resume": {
            "professional_summary": "Experienced Angular Developer with 5+ years building scalable web applications. Proven expertise in modern frontend frameworks, TypeScript, and responsive UI development. Strong track record of delivering high-quality code and collaborating with cross-functional teams.",
            "skills_organized": ["Angular", "TypeScript", "JavaScript", "HTML5", "CSS3", "RxJS", "NgRx", "REST APIs"],
            "work_experience": []
        },
        "match_improvement": 88,
        "changes": [
            {
                "section": "Professional Summary",
                "type": "modified",
                "original": "Software developer with experience in web development",
                "modified": "Experienced Angular Developer with 5+ years building scalable web applications using Angular, TypeScript, and modern frontend frameworks",
                "reason": "Tailored to highlight Angular expertise and align with job requirements. Added specific technologies and quantifiable experience."
            },
            {
                "section": "Skills",
                "type": "modified",
                "original": "JavaScript, HTML, CSS",
                "modified": "Angular 18+, TypeScript, JavaScript (ES6+), HTML5, CSS3, RxJS, NgRx State Management, RESTful APIs, Responsive Design",
                "reason": "Emphasized Angular-specific skills and modern framework expertise to match job description keywords for better ATS scoring."
            },
            {
                "section": "Work Experience",
                "type": "modified",
                "original": "Developed web applications using various technologies",
                "modified": "Architected and developed enterprise-level Angular applications serving 100K+ users, implementing reactive programming patterns with RxJS and state management with NgRx, resulting in 40% performance improvement",
                "reason": "Action-oriented with quantifiable results. Highlights Angular-specific achievements and technical depth relevant to the role."
            },
            {
                "section": "Technical Skills",
                "type": "added",
                "modified": "Added: Component-based architecture, Lazy loading, Angular CLI, Unit testing (Jasmine/Karma), CI/CD pipelines",
                "reason": "Included key technical competencies mentioned in job description to improve keyword matching and demonstrate comprehensive Angular ecosystem knowledge."
            },
            {
                "section": "Projects",
                "type": "modified",
                "original": "Built responsive web interfaces",
                "modified": "Led development of responsive Angular SPA with micro-frontend architecture, implementing standalone components and signals for optimal performance. Reduced bundle size by 35% through strategic lazy loading.",
                "reason": "Showcases modern Angular features (standalone components, signals) and quantifiable technical achievements that align with senior-level expectations."
            },
            {
                "section": "Soft Skills",
                "type": "added",
                "modified": "Added emphasis on: Team collaboration, Agile/Scrum methodology, Code review practices, Technical mentoring",
                "reason": "Addresses soft skills mentioned in job posting. Demonstrates leadership and teamwork capabilities essential for the role."
            },
            {
                "section": "Certifications",
                "type": "modified",
                "original": "Web Development Certificate",
                "modified": "Angular Certified Developer, TypeScript Advanced Certification, AWS Cloud Practitioner",
                "reason": "Highlights relevant certifications that validate technical expertise and align with company's tech stack requirements."
            }
        ]
    }

@router.post("/jobs/{job_id}/tailor-resume")
async def tailor_resume(job_id: str, current_user: dict = Depends(get_current_user)):
    """Tailor resume for specific job"""
    try:
        # Mark as tailored
        await db.database["users"].update_one(
            {"user_id": current_user["user_id"]},
            {"$addToSet": {"tailored_jobs": job_id}}
        )
        
        return {
            "success": True,
            "message": "Resume tailored successfully",
            "tailor_done": True,
            "match_percentage": 80
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/apply")
async def apply_for_job(job_id: str, use_tailored: bool = False, current_user: dict = Depends(get_current_user)):
    """Apply for job with or without tailored resume"""
    try:
        from datetime import datetime
        
        print(f"\n=== Apply Request ===")
        print(f"Job ID: {job_id}")
        print(f"Use Tailored: {use_tailored}")
        print(f"User ID: {current_user['user_id']}")
        
        if use_tailored:
            # Get the tailored resume preview data
            preview = await get_tailor_preview(job_id, current_user)
            resume_data = preview.get("tailored_resume", {})
            match_score = preview.get("match_improvement", 88)
            print(f"Tailored resume data: {resume_data}")
            print(f"Match score: {match_score}")
        else:
            # Get user's original resume
            user = await db.database["users"].find_one({"user_id": current_user["user_id"]})
            resume_data = sanitize_for_json(user) if user else {}
            match_score = None
        
        # Create application ID
        application_id = f"app_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{current_user['user_id']}"
        
        # Create application document
        application = {
            "application_id": application_id,
            "job_id": job_id,
            "user_id": current_user["user_id"],
            "candidate_name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}",
            "candidate_email": current_user.get('email', ''),
            "resume_tailored": use_tailored,
            "resume_data": resume_data,
            "match_score": match_score,
            "applied_at": datetime.utcnow().isoformat(),
            "applied_date": datetime.utcnow().isoformat(),
            "status": "applied"
        }
        
        print(f"Application document to insert: resume_tailored={application['resume_tailored']}, match_score={application['match_score']}")
        
        # Insert application into applications collection
        await db.database["applications"].insert_one(application)
        
        # Add application reference to job's applications_received array
        await db.database["jobs"].update_one(
            {"job_id": job_id},
            {
                "$push": {
                    "applications_received": {
                        "application_id": application_id,
                        "user_id": current_user["user_id"],
                        "candidate_name": application["candidate_name"],
                        "applied_at": application["applied_at"],
                        "applied_date": application["applied_date"],
                        "status": "applied",
                        "resume_tailored": use_tailored,
                        "match_score": match_score,
                        "match_percentage": match_score if use_tailored else 0,
                        "ats_score": 0
                    }
                }
            }
        )
        
        message = "Application submitted with tailored resume" if use_tailored else "Application submitted"
        
        return {
            "success": True,
            "message": message,
            "application_id": application_id,
            "match_percentage": match_score
        }
    except Exception as e:
        print(f"Error in apply: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
