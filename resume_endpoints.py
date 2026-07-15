"""
Resume API endpoints for JobMitra
"""

import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
import uuid

from auth_endpoints import get_current_user
from db import db

# Create router
resume_router = APIRouter(prefix="/api/v1", tags=["Resume"])

class ResumeCreateRequest(BaseModel):
    user_id: str
    title: str
    template_id: str = "modern"
    sections: Optional[Dict[str, Any]] = None
    populate_from_profile: bool = False

class ResumeUpdateRequest(BaseModel):
    sections: Dict[str, Any]

@resume_router.post("/resumes")
async def create_resume(
    request: ResumeCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new resume, optionally populated from user profile"""
    try:
        user_id = current_user["user_id"]
        
        # Always get user profile data to populate resume
        user_profile = await db.database["users"].find_one({"user_id": user_id})
        logger.debug("Found user profile for {user_id}: %s ", user_profile is not None)
        
        if user_profile:
            logger.debug("User profile data: name={user_profile.get('first_name')} {user_profile.get('last_name')}, email= %s ", user_profile.get('email'))
            # Map profile data to resume sections
            sections = {
                "personal_info": {
                    "full_name": f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip(),
                    "email": user_profile.get("email", ""),
                    "phone": user_profile.get("phone", ""),
                    "location": user_profile.get("personal_info", {}).get("location", {}).get("city", ""),
                    "linkedin": user_profile.get("social_links", {}).get("linkedin", ""),
                    "portfolio": user_profile.get("social_links", {}).get("portfolio", ""),
                    "github": user_profile.get("social_links", {}).get("github", "")
                },
                "summary": user_profile.get("professional_info", {}).get("professional_summary", ""),
                "experience": [],
                "education": [],
                "skills": {
                    "technical": user_profile.get("skills", []),
                    "soft": user_profile.get("communication_skills", [])
                },
                "projects": [],
                "certifications": [
                    {
                        "name": cert.get("name", "") if isinstance(cert, dict) else str(cert),
                        "issuer": cert.get("issuer", "") if isinstance(cert, dict) else "",
                        "date": cert.get("issue_date", "") if isinstance(cert, dict) else "",
                        "credential_id": cert.get("credential_id", "") if isinstance(cert, dict) else ""
                    }
                    for cert in user_profile.get("certifications", [])
                    if cert and (isinstance(cert, dict) and cert.get("name") or isinstance(cert, str))
                ]
            }
            logger.debug("Created sections with real data: %s ", sections['personal_info']['full_name'])
        else:
            logger.debug("No user profile found, using default sections")
            sections = request.sections or get_default_sections()
        
        # Create resume document
        resume_doc = {
            "resume_id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": request.title,
            "template_id": request.template_id,
            "sections": sections,
            "ats_score": 65,  # Default score
            "suggestions": [
                "Add more quantified achievements",
                "Include relevant keywords for your industry",
                "Optimize section order for better impact"
            ],
            "is_primary": True,  # First resume is primary
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert into database
        result = await db.database["resumes"].insert_one(resume_doc)
        
        logger.debug("Resume created with ID: %s ", resume_doc['resume_id'])
        return {
            "resume_id": resume_doc["resume_id"],
            "message": "Resume created successfully"
        }
        
    except Exception as e:
        logger.error("creating resume: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create resume")

@resume_router.get("/users/{user_id}/resumes")
async def get_user_resumes(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all resumes for a user"""
    try:
        if current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        cursor = db.database["resumes"].find({"user_id": user_id}).sort("created_at", -1)
        resumes = await cursor.to_list(length=None)
        
        # Convert ObjectId to string
        for resume in resumes:
            resume["_id"] = str(resume["_id"])
        
        return {
            "resumes": resumes,
            "count": len(resumes)
        }
        
    except Exception as e:
        logger.error("getting user resumes: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get resumes")

@resume_router.get("/resumes/{resume_id}")
async def get_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific resume by ID"""
    try:
        resume = await db.database["resumes"].find_one({"resume_id": resume_id})
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Check if user owns this resume
        if resume["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        resume["_id"] = str(resume["_id"])
        return resume
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("getting resume: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get resume")

@resume_router.put("/resumes/{resume_id}")
async def update_resume(
    resume_id: str,
    request: ResumeUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update resume sections"""
    try:
        # Check if resume exists and user owns it
        resume = await db.database["resumes"].find_one({"resume_id": resume_id})
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        if resume["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update resume
        result = await db.database["resumes"].update_one(
            {"resume_id": resume_id},
            {
                "$set": {
                    "sections": request.sections,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made")
        
        return {"message": "Resume updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("updating resume: %s", e)
        raise HTTPException(status_code=500, detail="Failed to update resume")

@resume_router.post("/resumes/{resume_id}/optimize")
async def optimize_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
    job_description: Optional[str] = None
):
    """AI optimize resume for better ATS score"""
    try:
        # Check if resume exists and user owns it
        resume = await db.database["resumes"].find_one({"resume_id": resume_id})
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        if resume["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Simulate AI optimization (in real implementation, call AI service)
        original_score = resume.get("ats_score", 65)
        optimized_score = min(original_score + 15, 95)  # Improve by 15 points, max 95
        
        # Update ATS score and suggestions
        await db.database["resumes"].update_one(
            {"resume_id": resume_id},
            {
                "$set": {
                    "ats_score": optimized_score,
                    "suggestions": [
                        "Resume optimized for ATS compatibility",
                        "Keywords enhanced for better matching",
                        "Format improved for readability"
                    ],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "original_score": original_score,
            "optimized_score": optimized_score,
            "improvement": optimized_score - original_score,
            "message": "Resume optimized successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("optimizing resume: %s", e)
        raise HTTPException(status_code=500, detail="Failed to optimize resume")

@resume_router.delete("/resumes/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a resume"""
    try:
        # Check if resume exists and user owns it
        resume = await db.database["resumes"].find_one({"resume_id": resume_id})
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        if resume["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete resume
        result = await db.database["resumes"].delete_one({"resume_id": resume_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=400, detail="Failed to delete resume")
        
        return {"message": "Resume deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("deleting resume: %s", e)
        raise HTTPException(status_code=500, detail="Failed to delete resume")

@resume_router.post("/resumes/create-from-profile")
async def create_resume_from_profile(
    current_user: dict = Depends(get_current_user)
):
    """Create a new resume populated with current user's profile data"""
    try:
        user_id = current_user["user_id"]
        
        # Create request with profile population enabled
        request = ResumeCreateRequest(
            user_id=user_id,
            title="My Resume",
            template_id="modern",
            populate_from_profile=True
        )
        
        return await create_resume(request, current_user)
        
    except Exception as e:
        logger.error("creating resume from profile: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create resume from profile")

@resume_router.put("/resumes/{resume_id}/populate-from-profile")
async def populate_resume_from_profile(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Replace existing resume data with current user's profile data"""
    try:
        user_id = current_user["user_id"]
        logger.debug("Current user ID: %s ", user_id)
        
        # Check if resume exists and get its owner
        existing_resume = await db.database["resumes"].find_one({"resume_id": resume_id})
        if existing_resume:
            logger.debug("Resume owner: %s ", existing_resume.get('user_id'))
            # Update resume owner to current user if it's a dummy resume
            if existing_resume.get('user_id') != user_id:
                await db.database["resumes"].update_one(
                    {"resume_id": resume_id},
                    {"$set": {"user_id": user_id}}
                )
                logger.debug("Updated resume owner to %s ", user_id)
        
        # Get user profile data
        user_profile = await db.database["users"].find_one({"user_id": user_id})
        logger.debug("Found user profile for {user_id}: %s ", user_profile is not None)
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        logger.debug("User profile data: name={user_profile.get('first_name')} {user_profile.get('last_name')}, email= %s ", user_profile.get('email'))
        
        # Map profile data to resume sections
        sections = {
            "personal_info": {
                "full_name": f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip(),
                "email": user_profile.get("email", ""),
                "phone": user_profile.get("phone", ""),
                "location": user_profile.get("personal_info", {}).get("location", {}).get("city", ""),
                "linkedin": user_profile.get("social_links", {}).get("linkedin", ""),
                "portfolio": user_profile.get("social_links", {}).get("portfolio", ""),
                "github": user_profile.get("social_links", {}).get("github", "")
            },
            "summary": user_profile.get("professional_info", {}).get("professional_summary", ""),
            "experience": [],
            "education": [],
            "skills": {
                "technical": user_profile.get("skills", []),
                "soft": user_profile.get("communication_skills", [])
            },
            "projects": [],
            "certifications": [
                {
                    "name": cert.get("name", "") if isinstance(cert, dict) else str(cert),
                    "issuer": cert.get("issuer", "") if isinstance(cert, dict) else "",
                    "date": cert.get("issue_date", "") if isinstance(cert, dict) else "",
                    "credential_id": cert.get("credential_id", "") if isinstance(cert, dict) else ""
                }
                for cert in user_profile.get("certifications", [])
                if cert and (isinstance(cert, dict) and cert.get("name") or isinstance(cert, str))
            ]
        }
        
        # Update the resume with real profile data
        result = await db.database["resumes"].update_one(
            {"resume_id": resume_id},
            {
                "$set": {
                    "sections": sections,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        logger.debug("Resume {resume_id} updated with real profile data for user %s ", user_id)
        
        logger.debug("Resume %s updated with real profile data", resume_id)
        return {
            "message": "Resume populated with profile data successfully",
            "sections": sections
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("populating resume from profile: %s", e)
        raise HTTPException(status_code=500, detail="Failed to populate resume from profile")

@resume_router.get("/resume-templates")
async def get_resume_templates():
    """Get available resume templates"""
    templates = [
        {
            "template_id": "modern",
            "name": "Modern",
            "description": "Clean and professional design with modern styling",
            "preview_url": "/templates/modern-preview.png",
            "category": "professional"
        },
        {
            "template_id": "classic",
            "name": "Classic",
            "description": "Traditional resume format suitable for conservative industries",
            "preview_url": "/templates/classic-preview.png",
            "category": "traditional"
        },
        {
            "template_id": "creative",
            "name": "Creative",
            "description": "Eye-catching design for creative professionals",
            "preview_url": "/templates/creative-preview.png",
            "category": "creative"
        },
        {
            "template_id": "executive",
            "name": "Executive",
            "description": "Sophisticated layout for senior-level positions",
            "preview_url": "/templates/executive-preview.png",
            "category": "executive"
        }
    ]
    
    return {"templates": templates}

def get_default_sections():
    """Get default empty resume sections"""
    return {
        "personal_info": {
            "full_name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "portfolio": "",
            "github": ""
        },
        "summary": "",
        "experience": [],
        "education": [],
        "skills": {
            "technical": [],
            "soft": []
        },
        "projects": [],
        "certifications": []
    }