"""
Dashboard and Profile API endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from job_db import JobDatabase

# Create router for dashboard and profile endpoints
router = APIRouter()

# Initialize job database
job_db = JobDatabase()


@router.get("/dashboard", tags=["Dashboard"])
async def get_dashboard():
    """Dashboard endpoint that returns data compatible with Angular frontend."""
    
    try:
        # Get real job statistics from database
        total_jobs = await job_db.get_total_job_count()
        active_jobs = await job_db.get_active_job_count()
    except Exception as e:
        # Fallback to mock data if database is not available
        total_jobs = 150
        active_jobs = 120
    
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
                "value": total_jobs,
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


@router.get("/profile/current", tags=["User Management"])
async def get_current_user_profile():
    """Get current user profile - returns dummy Indian profile data."""
    return {
        "user_id": "usr_001",
        "email": "priya.sharma@example.com",
        "full_name": "Priya Sharma",
        "phone": "+91 98765 43210",
        "current_job_title": "Senior Software Engineer",
        "desired_job_title": "Technical Lead",
        "experience_years": "4-5",
        "skills": [
            "JavaScript", "React", "Node.js", "Python", "MongoDB", 
            "AWS", "Docker", "Git", "TypeScript", "Express.js"
        ],
        "professional_summary": "Experienced software engineer with a passion for building scalable web applications. Skilled in full-stack development with expertise in modern JavaScript frameworks and cloud technologies. Looking to transition into a technical leadership role.",
        "certifications": [
            "AWS Certified Developer Associate",
            "Google Cloud Professional Developer",
            "Certified Kubernetes Administrator"
        ],
        "area_of_expertise": [
            "Full Stack Development",
            "Cloud Architecture", 
            "DevOps",
            "Team Leadership"
        ],
        "key_contributions": "Led the development of a microservices architecture that improved system performance by 40%. Mentored 3 junior developers and established coding standards for the team. Implemented CI/CD pipelines reducing deployment time by 60%.",
        "preferred_work_types": ["remote", "hybrid"],
        "preferred_employment_types": ["full-time"],
        "social_links": {
            "github": "https://github.com/priyasharma",
            "portfolio": "https://priyasharma.dev",
            "youtube": "https://youtube.com/@priyatech"
        },
        "location": {
            "city": "Bangalore, Karnataka",
            "country": "India",
            "type": "hybrid"
        },
        "expected_salary": {
            "min": 18,
            "max": 25,
            "currency": "INR",
            "period": "yearly"
        },
        "profile_completion_percentage": 92,
        "profile_views": 156,
        "last_active": "2024-07-29T14:22:00Z",
        "is_active": True,
        "is_public": True,
        "email_notifications": True,
        "profile_searchable": True,
        "preferred_locations": ["Bangalore", "Mumbai", "Remote"],
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-07-29T14:22:00Z"
    }


@router.get("/jobs", tags=["Jobs"])
async def get_job_listings(
    page: int = 1, 
    per_page: int = 10,
    keywords: str = None,
    location: str = None,
    experience_level: str = None,
    employment_type: str = None,
    job_type: str = None
):
    """Get job listings for job search page with pagination and filtering."""
    
    try:
        # Use the real database for job search
        search_filters = {}
        
        if keywords:
            search_filters["keywords"] = keywords
        if location and location != "all":
            search_filters["location"] = location
        if experience_level and experience_level != "all":
            search_filters["experience_level"] = experience_level.replace("-", "_")
        if employment_type and employment_type != "all":
            search_filters["employment_type"] = employment_type.replace("-", "_")
        if job_type and job_type != "all":
            search_filters["job_type"] = job_type.replace("-", "_")
            
        # Search jobs using database
        search_result = await job_db.search_jobs(
            filters=search_filters,
            page=page,
            limit=per_page
        )
        
        return {
            "jobs": search_result["jobs"],
            "total_count": search_result["total"],
            "page": page,
            "per_page": per_page,
            "total_pages": (search_result["total"] + per_page - 1) // per_page,
            "has_next": page * per_page < search_result["total"],
            "has_prev": page > 1,
            "filters": {
                "locations": ["All Locations", "Bangalore", "Mumbai", "Hyderabad", "Remote"],
                "experience_levels": ["All Levels", "entry", "junior", "mid", "senior", "lead", "executive"],
                "employment_types": ["All Types", "full_time", "part_time", "contract", "temporary", "internship"],
                "job_types": ["All Types", "remote", "onsite", "hybrid"],
                "companies": ["All Companies"],
                "salary_ranges": [
                    {"label": "All Ranges", "min": 0, "max": 10000000},
                    {"label": "₹10-15 LPA", "min": 1000000, "max": 1500000},
                    {"label": "₹15-20 LPA", "min": 1500000, "max": 2000000},
                    {"label": "₹20-25 LPA", "min": 2000000, "max": 2500000},
                    {"label": "₹25+ LPA", "min": 2500000, "max": 10000000}
                ]
            }
        }
        
    except Exception as e:
        print(f"Database error in job search: {e}")
        # Fallback to mock data if database fails
        return get_mock_job_listings(page, per_page, keywords, location, experience_level, employment_type, job_type)


def get_mock_job_listings(page, per_page, keywords, location, experience_level, employment_type, job_type):
    """Fallback mock job listings if database is unavailable."""
def get_mock_job_listings(page, per_page, keywords, location, experience_level, employment_type, job_type):
    """Fallback mock job listings if database is unavailable."""
    
    # Mock job data (same structure as before but with pagination logic)
    all_jobs = [
        {
            "_id": "6507f1f5e1234567890abcde",
            "job_id": "senior-software-engineer-techcorp",
            "title": "Senior Software Engineer",
            "company": "TechCorp Inc.",
            "location": {
                "city": "Bangalore",
                "state": "Karnataka",
                "country": "India",
                "is_remote": True,
                "timezone": "IST"
            },
            "employment_type": "full-time",
            "experience_level": "senior",
            "salary": {
                "min": 1800000,
                "max": 2500000,
                "currency": "INR",
                "period": "yearly",
                "is_negotiable": True
            },
            "description": "Join our team to build scalable AI-powered applications. We are looking for a Senior Software Engineer to help build next-generation AI-powered applications using React, Node.js, Python, and cloud services.",
            "requirements": [
                "5+ years of experience in software development",
                "Proficiency in JavaScript, Python, or Java",
                "Experience with React and Node.js",
                "Strong understanding of software architecture"
            ],
            "responsibilities": [
                "Design and develop scalable web applications",
                "Collaborate with product managers and designers",
                "Mentor junior developers",
                "Implement best practices and maintain code quality",
                "Optimize application performance",
                "Participate in code reviews and team meetings",
                "Set up and maintain CI/CD pipelines"
            ],
            "benefits": [
                "Health Insurance (Medical + Family)",
                "PF & ESI",
                "Flexible working hours",
                "Learning and development budget (₹1.5L annually)",
                "Work from home allowance",
                "Annual performance bonus"
            ],
            "skills_required": ["JavaScript", "React", "Node.js", "Python"],
            "skills_preferred": ["AWS", "Docker", "Kubernetes", "TypeScript"],
            "application_deadline": "2025-02-15T23:59:59Z",
            "company_info": {
                "company_size": "1000+",
                "industry": "Technology",
                "website": "https://techcorp.com",
                "description": "Leading AI and cloud solutions provider"
            },
            "job_type": "hybrid",
            "posted_date": "2025-01-15T09:00:00Z",
            "updated_date": "2025-01-20T15:30:00Z",
            "is_active": True,
            "tags": ["ai", "full-stack", "cloud", "remote-friendly"],
            "views_count": 245,
            "applications_count": 18,
            "match_percentage": 92,
            "hr_contact": {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@techcorp.com",
                "phone": "+91 98765 43210",
                "title": "Senior Technical Recruiter",
                "department": "Human Resources"
            },
            "learning_resources": [
                {
                    "id": "lr-001",
                    "title": "React Advanced Patterns and Best Practices",
                    "description": "Learn advanced React patterns including render props, higher-order components, and custom hooks",
                    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "duration": "45:30",
                    "level": "advanced",
                    "channel": "Tech Academy",
                    "skill": "React",
                    "rating": 4.8
                }
            ]
        },
        {
            "_id": "6507f1f5e1234567890abcdf",
            "job_id": "product-manager-innovateai",
            "title": "Product Manager",
            "company": "InnovateAI",
            "location": {
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "is_remote": False,
                "timezone": "IST"
            },
            "employment_type": "full-time",
            "experience_level": "mid",
            "salary": {
                "min": 1200000,
                "max": 1800000,
                "currency": "INR",
                "period": "yearly",
                "is_negotiable": True
            },
            "description": "Lead product strategy for our AI recruitment platform. Work with engineering, design, and business teams to define product requirements and ensure successful launches.",
            "requirements": [
                "3+ years of product management experience",
                "Experience with SaaS products",
                "Understanding of AI/ML concepts",
                "Strong analytical and problem-solving skills"
            ],
            "responsibilities": [
                "Define product strategy and roadmap",
                "Work with engineering and design teams",
                "Conduct user research and gather feedback",
                "Analyze product metrics and performance",
                "Manage product launches and feature rollouts"
            ],
            "benefits": [
                "Health Insurance",
                "Equity participation",
                "Flexible work arrangements",
                "Learning budget"
            ],
            "skills_required": ["Product Management", "Analytics", "User Research"],
            "skills_preferred": ["SQL", "A/B Testing", "Agile", "Figma"],
            "application_deadline": "2025-02-20T23:59:59Z",
            "company_info": {
                "company_size": "501-1000",
                "industry": "Artificial Intelligence",
                "website": "https://innovateai.com",
                "description": "AI-powered recruitment and HR solutions"
            },
            "job_type": "onsite",
            "posted_date": "2025-01-18T10:00:00Z",
            "updated_date": "2025-01-22T11:15:00Z",
            "is_active": True,
            "tags": ["product-management", "ai", "saas", "analytics"],
            "views_count": 198,
            "applications_count": 12,
            "match_percentage": 85,
            "hr_contact": {
                "name": "Rahul Gupta",
                "email": "rahul.gupta@innovateai.com",
                "phone": "+91 98765 43211",
                "title": "Product Talent Acquisition Lead",
                "department": "People Operations"
            },
            "learning_resources": [
                {
                    "id": "lr-003",
                    "title": "Product Management Fundamentals",
                    "description": "Complete guide to product management strategy and execution",
                    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "duration": "58:20",
                    "level": "intermediate",
                    "channel": "Product School",
                    "skill": "Product Management",
                    "rating": 4.6
                }
            ]
        },
        {
            "_id": "6507f1f5e1234567890abce0",
            "job_id": "frontend-developer-dataflow",
            "title": "Frontend Developer",
            "company": "DataFlow Solutions",
            "location": {
                "city": "Remote",
                "state": "",
                "country": "India",
                "is_remote": True,
                "timezone": "IST"
            },
            "employment_type": "full-time",
            "experience_level": "mid",
            "salary": {
                "min": 1000000,
                "max": 1500000,
                "currency": "INR",
                "period": "yearly",
                "is_negotiable": True
            },
            "description": "Build beautiful and responsive web applications using modern frontend technologies. Work with our design team to create intuitive user experiences.",
            "requirements": [
                "3+ years of frontend development experience",
                "Proficiency in React and TypeScript",
                "Experience with modern CSS frameworks",
                "Understanding of responsive design principles"
            ],
            "responsibilities": [
                "Develop responsive web applications",
                "Collaborate with designers and backend developers",
                "Optimize application performance",
                "Write clean, maintainable code",
                "Participate in code reviews"
            ],
            "benefits": [
                "Remote work flexibility",
                "Health insurance",
                "Professional development budget",
                "Modern tech stack"
            ],
            "skills_required": ["React", "TypeScript", "CSS", "HTML"],
            "skills_preferred": ["Next.js", "Tailwind CSS", "Git", "Figma"],
            "application_deadline": "2025-02-10T23:59:59Z",
            "company_info": {
                "company_size": "51-200",
                "industry": "Data Analytics",
                "website": "https://dataflow.com",
                "description": "Advanced data analytics and machine learning platform"
            },
            "job_type": "remote",
            "posted_date": "2025-01-20T14:00:00Z",
            "updated_date": "2025-01-25T09:30:00Z",
            "is_active": True,
            "tags": ["frontend", "react", "data-viz", "remote"],
            "views_count": 156,
            "applications_count": 8,
            "match_percentage": 78,
            "hr_contact": {
                "name": "Priya Patel",
                "email": "priya.patel@dataflow.com",
                "phone": "+91 98765 43212",
                "title": "Engineering Recruiter",
                "department": "Talent Acquisition"
            },
            "learning_resources": [
                {
                    "id": "lr-004",
                    "title": "Advanced TypeScript for React Developers",
                    "description": "Master TypeScript patterns for building robust React applications",
                    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "duration": "1:05:15",
                    "level": "advanced",
                    "channel": "TypeScript Pro",
                    "skill": "TypeScript",
                    "rating": 4.7
                }
            ]
        },
        {
            "_id": "6507f1f5e1234567890abce1",
            "job_id": "devops-engineer-fintech",
            "title": "DevOps Engineer",
            "company": "FinTech Solutions",
            "location": {
                "city": "Hyderabad",
                "state": "Telangana",
                "country": "India",
                "is_remote": False,
                "timezone": "IST"
            },
            "employment_type": "full-time",
            "experience_level": "senior",
            "salary": {
                "min": 1600000,
                "max": 2200000,
                "currency": "INR",
                "period": "yearly",
                "is_negotiable": True
            },
            "description": "Manage and optimize our cloud infrastructure. Design and implement CI/CD pipelines, ensure system reliability and security.",
            "requirements": [
                "5+ years of DevOps experience",
                "Strong knowledge of AWS/Azure",
                "Experience with Kubernetes and Docker",
                "Understanding of security best practices"
            ],
            "responsibilities": [
                "Manage cloud infrastructure",
                "Design CI/CD pipelines",
                "Monitor system performance",
                "Implement security measures",
                "Automate deployment processes"
            ],
            "benefits": [
                "Competitive salary",
                "Stock options",
                "Health insurance",
                "Technical training budget"
            ],
            "skills_required": ["AWS", "Kubernetes", "Docker", "Linux"],
            "skills_preferred": ["Terraform", "Jenkins", "Monitoring", "Python"],
            "application_deadline": "2025-02-25T23:59:59Z",
            "company_info": {
                "company_size": "201-500",
                "industry": "Financial Technology",
                "website": "https://fintech-solutions.com",
                "description": "Digital banking and payment solutions"
            },
            "job_type": "hybrid",
            "posted_date": "2025-01-22T08:00:00Z",
            "updated_date": "2025-01-26T16:45:00Z",
            "is_active": True,
            "tags": ["devops", "cloud", "fintech", "security"],
            "views_count": 134,
            "applications_count": 15,
            "match_percentage": 88,
            "hr_contact": {
                "name": "Anjali Reddy",
                "email": "anjali.reddy@fintech-solutions.com",
                "phone": "+91 98765 43213",
                "title": "DevOps Talent Partner",
                "department": "Engineering Recruitment"
            },
            "learning_resources": [
                {
                    "id": "lr-006",
                    "title": "Kubernetes Deployment Strategies",
                    "description": "Master Kubernetes deployments and orchestration",
                    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "duration": "1:45:20",
                    "level": "advanced",
                    "channel": "Cloud Native Academy",
                    "skill": "Kubernetes",
                    "rating": 4.9
                }
            ]
        }
    ]
    
    # Apply filters to the job list
    filtered_jobs = all_jobs.copy()
    
    # Filter by keywords (search in title, company, description, skills)
    if keywords:
        keywords_lower = keywords.lower()
        filtered_jobs = [job for job in filtered_jobs if 
            keywords_lower in job["title"].lower() or
            keywords_lower in job["company"].lower() or
            keywords_lower in job["description"].lower() or
            any(keywords_lower in skill.lower() for skill in job.get("skills_required", [])) or
            any(keywords_lower in skill.lower() for skill in job.get("skills_preferred", []))
        ]
    
    # Filter by location
    if location and location != "all":
        location_lower = location.lower().replace("-", " ")
        filtered_jobs = [job for job in filtered_jobs if 
            location_lower in job["location"]["city"].lower() or
            location_lower in job["location"]["state"].lower() or
            location_lower in job["location"]["country"].lower() or
            (location_lower == "remote" and job["location"]["is_remote"])
        ]
    
    # Filter by experience level
    if experience_level and experience_level != "all":
        experience_level_clean = experience_level.lower().replace("-", " ")
        filtered_jobs = [job for job in filtered_jobs if 
            job["experience_level"].lower() == experience_level_clean
        ]
    
    # Filter by employment type
    if employment_type and employment_type != "all":
        employment_type_clean = employment_type.lower().replace("-", " ")
        filtered_jobs = [job for job in filtered_jobs if 
            job["employment_type"].lower() == employment_type_clean
        ]
    
    # Filter by job type
    if job_type and job_type != "all":
        job_type_clean = job_type.lower().replace("-", " ")
        filtered_jobs = [job for job in filtered_jobs if 
            job["job_type"].lower() == job_type_clean
        ]
    
    # Calculate pagination on filtered results
    total_jobs = len(filtered_jobs)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_jobs = filtered_jobs[start_idx:end_idx]
    
    total_pages = (total_jobs + per_page - 1) // per_page
    has_next = end_idx < total_jobs
    has_prev = page > 1
    
    return {
        "jobs": paginated_jobs,
        "total_count": total_jobs,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "filters": {
            "locations": ["All Locations", "Bangalore", "Mumbai", "Hyderabad", "Remote"],
            "experience_levels": ["All Levels", "entry", "mid", "senior", "lead"],
            "employment_types": ["All Types", "full-time", "part-time", "contract"],
            "job_types": ["All Types", "remote", "onsite", "hybrid"],
            "companies": ["All Companies", "TechCorp Inc.", "InnovateAI", "DataFlow Solutions", "FinTech Solutions"],
            "salary_ranges": [
                {"label": "All Ranges", "min": 0, "max": 10000000},
                {"label": "₹10-15 LPA", "min": 1000000, "max": 1500000},
                {"label": "₹15-20 LPA", "min": 1500000, "max": 2000000},
                {"label": "₹20-25 LPA", "min": 2000000, "max": 2500000},
                {"label": "₹25+ LPA", "min": 2500000, "max": 10000000}
            ]
        }
    }


@router.get("/applications", tags=["Applications"])
async def get_applications(page: int = 1, per_page: int = 10):
    """Get user applications with pagination."""
    
    # Mock applications data
    applications = [
        {
            "_id": "app_1",
            "application_id": "app_1",
            "user_id": "user_1",
            "job_id": "job_1",
            "job_title": "Senior Software Engineer",
            "company": "TechCorp Inc.",
            "status": "under_review",
            "applied_date": "2025-03-15T08:00:00Z",
            "last_updated": "2025-03-20T10:30:00Z",
            "resume_url": "https://example.com/resume.pdf",
            "cover_letter": "I am excited to apply for this Senior Software Engineer position at TechCorp Inc. With over 5 years of experience in full-stack development...",
            "application_source": "direct",
            "interview_stages": [
                {
                    "stage_id": "stage_1",
                    "stage_name": "Technical Screening",
                    "stage_type": "phone",
                    "scheduled_date": "2025-03-25T14:00:00Z",
                    "status": "scheduled",
                    "interviewer": "Sarah Johnson - Tech Lead",
                    "notes": "45-minute technical discussion"
                }
            ],
            "follow_up_dates": ["2025-03-22T09:00:00Z"],
            "notes": "Applied through company website. Strong match for React and Node.js requirements.",
            "priority": "high",
            "tags": ["react", "nodejs", "senior", "fullstack"],
            "progress_percentage": 50
        },
        {
            "_id": "app_2", 
            "application_id": "app_2",
            "user_id": "user_1",
            "job_id": "job_2",
            "job_title": "Product Manager",
            "company": "InnovateAI",
            "status": "interview_scheduled",
            "applied_date": "2025-03-12T10:00:00Z",
            "last_updated": "2025-03-18T15:45:00Z",
            "application_source": "referral",
            "referral_info": {
                "referrer_name": "Alex Chen",
                "referrer_contact": "alex.chen@innovateai.com",
                "relationship": "Former colleague"
            },
            "interview_stages": [
                {
                    "stage_id": "stage_1",
                    "stage_name": "Initial HR Screening",
                    "stage_type": "video",
                    "completed_date": "2025-03-16T11:00:00Z",
                    "status": "completed",
                    "interviewer": "Maria Rodriguez - HR",
                    "feedback": "Good cultural fit, strong communication skills"
                },
                {
                    "stage_id": "stage_2",
                    "stage_name": "Product Management Interview",
                    "stage_type": "video",
                    "scheduled_date": "2025-03-22T14:00:00Z",
                    "status": "scheduled",
                    "interviewer": "David Kim - VP Product",
                    "notes": "Case study discussion and product strategy"
                }
            ],
            "follow_up_dates": [],
            "notes": "Referred by Alex Chen. Interview went well, waiting for next round.",
            "priority": "high",
            "tags": ["product", "ai", "strategy", "senior"],
            "progress_percentage": 75
        },
        {
            "_id": "app_3",
            "application_id": "app_3", 
            "user_id": "user_1",
            "job_id": "job_3",
            "job_title": "Frontend Developer",
            "company": "WebSolutions",
            "status": "rejected",
            "applied_date": "2025-03-08T09:30:00Z",
            "last_updated": "2025-03-14T16:20:00Z",
            "application_source": "job_board",
            "interview_stages": [
                {
                    "stage_id": "stage_1",
                    "stage_name": "Technical Assessment",
                    "stage_type": "coding",
                    "completed_date": "2025-03-10T10:00:00Z",
                    "status": "completed",
                    "feedback": "Code quality was good but didn't meet senior level expectations"
                }
            ],
            "follow_up_dates": [],
            "notes": "Applied through Indeed. Unfortunately not selected after technical assessment.",
            "priority": "medium",
            "tags": ["frontend", "react", "junior"],
            "rejection_feedback": "Thank you for your interest. While your technical skills are solid, we're looking for someone with more senior-level experience.",
            "progress_percentage": 100
        },
        {
            "_id": "app_4",
            "application_id": "app_4",
            "user_id": "user_1", 
            "job_id": "job_4",
            "job_title": "Full Stack Developer",
            "company": "StartupXYZ",
            "status": "applied",
            "applied_date": "2025-03-20T11:15:00Z",
            "last_updated": "2025-03-20T11:15:00Z",
            "application_source": "company_website",
            "interview_stages": [],
            "follow_up_dates": ["2025-03-27T09:00:00Z"],
            "notes": "Recently applied. Good company culture and growth potential.",
            "priority": "medium",
            "tags": ["fullstack", "startup", "growth"],
            "progress_percentage": 25
        },
        {
            "_id": "app_5",
            "application_id": "app_5",
            "user_id": "user_1",
            "job_id": "job_5", 
            "job_title": "DevOps Engineer",
            "company": "CloudTech Solutions",
            "status": "offer_received",
            "applied_date": "2025-02-28T14:00:00Z",
            "last_updated": "2025-03-19T09:30:00Z",
            "application_source": "referral",
            "interview_stages": [
                {
                    "stage_id": "stage_1",
                    "stage_name": "Technical Phone Screen",
                    "stage_type": "phone",
                    "completed_date": "2025-03-05T15:00:00Z",
                    "status": "completed",
                    "interviewer": "Mike Wilson - DevOps Lead"
                },
                {
                    "stage_id": "stage_2", 
                    "stage_name": "System Design Interview",
                    "stage_type": "video",
                    "completed_date": "2025-03-12T16:00:00Z",
                    "status": "completed",
                    "interviewer": "Lisa Park - Engineering Manager"
                },
                {
                    "stage_id": "stage_3",
                    "stage_name": "Final Interview",
                    "stage_type": "onsite",
                    "completed_date": "2025-03-17T10:00:00Z", 
                    "status": "completed",
                    "interviewer": "John Davis - CTO"
                }
            ],
            "offer_details": {
                "salary": 2200000,
                "currency": "INR",
                "benefits": ["Health Insurance", "PF & ESI", "Remote Work", "Learning Budget", "Annual Bonus"],
                "start_date": "2025-04-01T00:00:00Z",
                "negotiation_status": "pending"
            },
            "follow_up_dates": [],
            "notes": "Excellent interview process. Offer received with competitive package.",
            "priority": "high",
            "tags": ["devops", "cloud", "senior", "remote"],
            "progress_percentage": 100
        }
    ]
    
    # Calculate pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_applications = applications[start_idx:end_idx]
    
    return {
        "applications": paginated_applications,
        "total_count": len(applications),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(applications) + per_page - 1) // per_page,
        "has_next": end_idx < len(applications),
        "has_prev": page > 1
    }
