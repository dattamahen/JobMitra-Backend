"""
Dashboard and Profile API endpoints.
"""

from datetime import datetime
from fastapi import APIRouter


# Create router for dashboard and profile endpoints
router = APIRouter()


@router.get("/dashboard", tags=["Dashboard"])
async def get_dashboard():
    """Dashboard endpoint that returns data compatible with Angular frontend."""
    
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
async def get_job_listings():
    """Get job listings for job search page."""
    
    return {
        "jobs": [
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
                    "Implement CI/CD pipelines"
                ],
                "skills_required": ["JavaScript", "React", "Node.js", "Python"],
                "skills_preferred": ["AWS", "Docker", "Kubernetes", "TypeScript"],
                "benefits": [
                    "Health Insurance (Medical + Family)",
                    "PF & ESI",
                    "Flexible working hours",
                    "Learning and development budget (₹1.5L annually)",
                    "Work from home allowance",
                    "Annual performance bonus"
                ],
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
                    },
                    {
                        "id": "lr-002", 
                        "title": "Node.js Microservices Architecture",
                        "description": "Build scalable microservices with Node.js and Docker",
                        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "duration": "1:12:45",
                        "level": "intermediate",
                        "channel": "Code Masters",
                        "skill": "Node.js",
                        "rating": 4.6
                    }
                ]
            },
            {
                "_id": "6507f1f5e1234567890abcdf",
                "job_id": "product-manager-innovateai",
                "title": "Senior Product Manager",
                "company": "InnovateAI",
                "location": {
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "country": "India", 
                    "is_remote": False,
                    "timezone": "IST"
                },
                "employment_type": "full-time",
                "experience_level": "senior",
                "salary": {
                    "min": 2200000,
                    "max": 3000000,
                    "currency": "INR",
                    "period": "yearly",
                    "is_negotiable": True
                },
                "description": "Lead product strategy and development for our AI-powered recruitment platform. Drive product vision, roadmap, and work closely with engineering teams.",
                "requirements": [
                    "5+ years of product management experience",
                    "Experience with SaaS products",
                    "Strong analytical and data-driven decision making",
                    "Excellent communication and leadership skills"
                ],
                "responsibilities": [
                    "Define product strategy and roadmap",
                    "Collaborate with engineering and design teams",
                    "Analyze user feedback and market trends",
                    "Drive product launches and go-to-market strategies"
                ],
                "skills_required": ["Product Management", "Data Analysis", "Leadership", "Strategic Planning"],
                "skills_preferred": ["AI/ML Knowledge", "B2B SaaS", "Agile", "SQL"],
                "benefits": [
                    "Comprehensive health insurance (Family covered)",
                    "Employee stock options (ESOP)",
                    "Professional development budget (₹2L annually)",
                    "Paid leave (25 days annually)",
                    "PF & Gratuity"
                ],
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
                "tags": ["product-management", "ai", "saas", "b2b"],
                "views_count": 189,
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
                        "rating": 4.7
                    }
                ]
            },
            {
                "_id": "6507f1f5e1234567890abce0",
                "job_id": "frontend-developer-startup",
                "title": "Frontend Developer", 
                "company": "DataFlow Solutions",
                "location": {
                    "city": "Pune",
                    "state": "Maharashtra",
                    "country": "India",
                    "is_remote": True,
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
                "description": "Build modern web applications using React and TypeScript. Work on data visualization dashboards and user interfaces for our analytics platform.",
                "requirements": [
                    "3+ years of React development experience",
                    "Strong knowledge of TypeScript",
                    "Experience with data visualization libraries",
                    "Understanding of modern CSS frameworks"
                ],
                "responsibilities": [
                    "Develop responsive web applications",
                    "Create interactive data visualizations",
                    "Optimize application performance",
                    "Collaborate with backend developers"
                ],
                "skills_required": ["React", "TypeScript", "JavaScript", "CSS"],
                "skills_preferred": ["D3.js", "Chart.js", "Material-UI", "Next.js"],
                "benefits": [
                    "Health insurance (Family + Parents)",
                    "Remote work flexibility", 
                    "Learning stipend (₹1L annually)",
                    "Performance bonuses (up to 3 months salary)",
                    "PF & Medical insurance"
                ],
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
                        "rating": 4.9
                    },
                    {
                        "id": "lr-005",
                        "title": "D3.js Data Visualization Masterclass",
                        "description": "Create stunning interactive data visualizations with D3.js",
                        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "duration": "2:15:30",
                        "level": "intermediate",
                        "channel": "Viz Academy",
                        "skill": "D3.js",
                        "rating": 4.5
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
                "experience_level": "mid",
                "salary": {
                    "min": 1500000,
                    "max": 2200000,
                    "currency": "INR",
                    "period": "yearly",
                    "is_negotiable": True
                },
                "description": "Manage cloud infrastructure and deployment pipelines for financial applications. Ensure high availability and security compliance.",
                "requirements": [
                    "4+ years of DevOps experience",
                    "Strong knowledge of AWS or Azure",
                    "Experience with Docker and Kubernetes",
                    "Understanding of CI/CD pipelines"
                ],
                "responsibilities": [
                    "Manage cloud infrastructure",
                    "Implement CI/CD pipelines",
                    "Monitor system performance",
                    "Ensure security compliance"
                ],
                "skills_required": ["AWS", "Docker", "Kubernetes", "CI/CD"],
                "skills_preferred": ["Terraform", "Jenkins", "Monitoring", "Security"],
                "benefits": [
                    "Comprehensive health coverage (Family + Parents)",
                    "Stock options (ESOP)",
                    "Certification reimbursement (₹3L annually)",
                    "Flexible hours + Work from home",
                    "PF, Gratuity & Bonus"
                ],
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
                        "rating": 4.8
                    },
                    {
                        "id": "lr-007",
                        "title": "AWS DevOps Best Practices",
                        "description": "Learn AWS DevOps tools and best practices for CI/CD",
                        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "duration": "1:28:45",
                        "level": "intermediate",
                        "channel": "AWS Training",
                        "skill": "AWS",
                        "rating": 4.7
                    }
                ]
            }
        ],
        "filters": {
            "locations": ["Bangalore", "Mumbai", "Pune", "Hyderabad", "Delhi", "Chennai", "Remote"],
            "experience_levels": ["entry", "mid", "senior", "lead", "executive"],
            "employment_types": ["full-time", "part-time", "contract", "freelance", "internship"],
            "job_types": ["remote", "hybrid", "onsite"],
            "companies": ["TechCorp Inc.", "InnovateAI", "DataFlow Solutions", "FinTech Solutions"],
            "salary_ranges": [
                {"label": "10-15 LPA", "min": 1000000, "max": 1500000},
                {"label": "15-20 LPA", "min": 1500000, "max": 2000000},
                {"label": "20-25 LPA", "min": 2000000, "max": 2500000},
                {"label": "25+ LPA", "min": 2500000, "max": 10000000}
            ]
        },
        "total_count": 4,
        "page": 1,
        "per_page": 10
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
