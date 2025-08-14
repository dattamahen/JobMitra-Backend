"""
Create test users with new schema and test authentication
"""

import asyncio
from datetime import datetime
from db_simple import db
from auth_utils import hash_password
import uuid

USERS_COLLECTION = "users"

async def create_test_users():
    """Create test users with the new comprehensive schema"""
    try:
        print("🔄 Creating test users with new schema...")
        
        await db.connect_to_mongo()
        
        # Test users data
        test_users = [
            {
                # User 1 - Candidate
                "user_id": "user001",
                "email": "user001@test.com",
                "password_hash": hash_password("test1234"),
                
                # Basic Personal Information
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": datetime(1992, 5, 15),
                "phone": "+1234567890",
                
                # Professional Information
                "overall_experience_years": 3,
                "highest_qualification": "Bachelor of Computer Science",
                "previous_organizations": [
                    {
                        "company_name": "StartupCorp",
                        "position": "Junior Developer",
                        "duration": "2021-2023",
                        "description": "Full-stack development with React and Node.js"
                    }
                ],
                "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Python"],
                "certifications": [
                    {
                        "name": "AWS Certified Developer",
                        "issuer": "Amazon Web Services",
                        "issue_date": datetime(2023, 3, 15),
                        "credential_id": "AWS-DEV-001"
                    }
                ],
                "contributions": "Developed 3 major features, mentored 2 junior developers",
                "communication_skills": [
                    {"skill": "Presentation", "level": "intermediate"},
                    {"skill": "Technical Writing", "level": "advanced"}
                ],
                "ai_tools": ["GitHub Copilot", "ChatGPT", "Claude"],
                
                # Social Links
                "social_links": {
                    "github": "https://github.com/user001",
                    "youtube": None,
                    "linkedin": "https://linkedin.com/in/user001",
                    "playstore": None
                },
                
                # Job Application Tracking
                "overall_jobs_applied": [],
                
                # User Classification
                "user_type": "candidate",
                "user_status": "active",
                "user_plan": "free",
                
                # Preferences
                "job_preferences": ["remote", "hybrid"],
                "employment_type": ["full-time"],
                
                # Timestamps
                "profile_created_on": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                
                # Analytics and Metrics
                "match_analysis_count": 5,
                "match_tailored_count": 3,
                "mock_interview_count": 2,
                "profile_completion_count": 85,
                "profile_visits": 12,
                "recent_activity": [
                    {
                        "activity_type": "profile_update",
                        "description": "Updated skills section",
                        "timestamp": datetime.utcnow(),
                        "metadata": {"section": "skills"}
                    }
                ],
                
                # Legacy compatibility
                "username": "user001",
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": None,
                
                # Legacy structure for backward compatibility
                "personal_info": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1234567890",
                    "location": {
                        "city": "San Francisco",
                        "state": "CA",
                        "country": "USA"
                    }
                },
                "professional_info": {
                    "current_role": "Software Developer",
                    "current_company": "TechCorp",
                    "total_experience": "3 years",
                    "industry": "Technology",
                    "skills": ["JavaScript", "React", "Node.js"],
                    "current_salary": 75000,
                    "expected_salary": 85000
                },
                "preferences": {
                    "job_locations": ["San Francisco", "Remote"],
                    "remote_preference": "hybrid",
                    "notice_period": "30 days"
                }
            },
            {
                # User 2 - Candidate
                "user_id": "user002",
                "email": "user002@test.com",
                "password_hash": hash_password("test1234"),
                
                # Basic Personal Information
                "first_name": "Jane",
                "last_name": "Smith",
                "date_of_birth": datetime(1990, 8, 22),
                "phone": "+1987654321",
                
                # Professional Information
                "overall_experience_years": 5,
                "highest_qualification": "Master of Computer Science",
                "previous_organizations": [
                    {
                        "company_name": "BigTech Inc",
                        "position": "Senior Frontend Developer",
                        "duration": "2020-2024",
                        "description": "Led frontend team, implemented design system"
                    },
                    {
                        "company_name": "WebAgency",
                        "position": "Frontend Developer",
                        "duration": "2018-2020",
                        "description": "Built responsive web applications"
                    }
                ],
                "skills": ["JavaScript", "TypeScript", "Angular", "React", "Vue.js", "CSS", "HTML"],
                "certifications": [
                    {
                        "name": "Google Cloud Professional",
                        "issuer": "Google Cloud",
                        "issue_date": datetime(2023, 6, 10),
                        "credential_id": "GCP-PRO-002"
                    },
                    {
                        "name": "Certified Scrum Master",
                        "issuer": "Scrum Alliance",
                        "issue_date": datetime(2022, 11, 5),
                        "credential_id": "CSM-002"
                    }
                ],
                "contributions": "Led team of 4 developers, implemented CI/CD pipeline, reduced deployment time by 50%",
                "communication_skills": [
                    {"skill": "Team Leadership", "level": "advanced"},
                    {"skill": "Client Communication", "level": "expert"}
                ],
                "ai_tools": ["GitHub Copilot", "ChatGPT", "Figma AI", "Cursor"],
                
                # Social Links
                "social_links": {
                    "github": "https://github.com/user002",
                    "youtube": "https://youtube.com/@janesmith-dev",
                    "linkedin": "https://linkedin.com/in/janesmith",
                    "playstore": None
                },
                
                # Job Application Tracking
                "overall_jobs_applied": ["job001", "job002"],
                
                # User Classification
                "user_type": "candidate",
                "user_status": "active",
                "user_plan": "subscribed",
                
                # Preferences
                "job_preferences": ["remote"],
                "employment_type": ["full-time", "contract"],
                
                # Timestamps
                "profile_created_on": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                
                # Analytics and Metrics
                "match_analysis_count": 15,
                "match_tailored_count": 8,
                "mock_interview_count": 5,
                "profile_completion_count": 95,
                "profile_visits": 28,
                "recent_activity": [
                    {
                        "activity_type": "application",
                        "description": "Applied to Senior Frontend Developer position",
                        "timestamp": datetime.utcnow(),
                        "metadata": {"job_id": "job001", "company": "TechStartup"}
                    }
                ],
                
                # Legacy compatibility
                "username": "user002",
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": None,
                
                # Legacy structure for backward compatibility
                "personal_info": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "phone": "+1987654321",
                    "location": {
                        "city": "New York",
                        "state": "NY",
                        "country": "USA"
                    }
                },
                "professional_info": {
                    "current_role": "Senior Frontend Developer",
                    "current_company": "BigTech Inc",
                    "total_experience": "5 years",
                    "industry": "Technology",
                    "skills": ["JavaScript", "TypeScript", "Angular"],
                    "current_salary": 95000,
                    "expected_salary": 110000
                },
                "preferences": {
                    "job_locations": ["New York", "Remote"],
                    "remote_preference": "remote",
                    "notice_period": "45 days"
                }
            },
            {
                # HR 1
                "user_id": "hr001",
                "email": "hr001@test.com",
                "password_hash": hash_password("test1234"),
                
                # Basic Personal Information
                "first_name": "Sarah",
                "last_name": "Johnson",
                "date_of_birth": datetime(1985, 3, 10),
                "phone": "+1555123456",
                
                # Professional Information
                "overall_experience_years": 8,
                "highest_qualification": "MBA in Human Resources",
                "previous_organizations": [
                    {
                        "company_name": "Global Corp",
                        "position": "Senior HR Manager",
                        "duration": "2019-2024",
                        "description": "Managed recruitment for 200+ employees"
                    }
                ],
                "skills": ["Recruitment", "Employee Relations", "Performance Management", "HR Analytics"],
                "certifications": [
                    {
                        "name": "SHRM Certified Professional",
                        "issuer": "Society for Human Resource Management",
                        "issue_date": datetime(2020, 4, 15),
                        "credential_id": "SHRM-CP-001"
                    }
                ],
                "contributions": "Reduced hiring time by 40%, implemented new onboarding process",
                "communication_skills": [
                    {"skill": "Interviewing", "level": "expert"},
                    {"skill": "Negotiation", "level": "advanced"}
                ],
                "ai_tools": ["LinkedIn Recruiter", "HiringSolved", "ChatGPT"],
                
                # Social Links
                "social_links": {
                    "github": None,
                    "youtube": None,
                    "linkedin": "https://linkedin.com/in/sarahjohnson-hr",
                    "playstore": None
                },
                
                # Job Application Tracking
                "overall_jobs_applied": [],
                
                # User Classification
                "user_type": "hire",
                "user_status": "active",
                "user_plan": "pro",
                
                # Preferences
                "job_preferences": ["hybrid"],
                "employment_type": ["full-time"],
                
                # Timestamps
                "profile_created_on": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                
                # Analytics and Metrics
                "match_analysis_count": 25,
                "match_tailored_count": 15,
                "mock_interview_count": 0,
                "profile_completion_count": 90,
                "profile_visits": 45,
                "recent_activity": [
                    {
                        "activity_type": "interview",
                        "description": "Conducted interview for Software Engineer position",
                        "timestamp": datetime.utcnow(),
                        "metadata": {"candidate_id": "user001", "position": "Software Engineer"}
                    }
                ],
                
                # Legacy compatibility
                "username": "hr001",
                "company_name": "TechCorp Solutions",
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": None,
                
                # Legacy structure for backward compatibility
                "personal_info": {
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "phone": "+1555123456",
                    "location": {
                        "city": "Boston",
                        "state": "MA",
                        "country": "USA"
                    }
                },
                "professional_info": {
                    "current_role": "HR Manager",
                    "current_company": "TechCorp Solutions",
                    "total_experience": "8 years",
                    "industry": "Human Resources",
                    "skills": ["Recruitment", "Employee Relations"],
                    "current_salary": 85000,
                    "expected_salary": 95000
                },
                "preferences": {
                    "job_locations": ["Boston", "Remote"],
                    "remote_preference": "hybrid",
                    "notice_period": "60 days"
                }
            },
            {
                # HR 2
                "user_id": "hr002",
                "email": "hr002@test.com",
                "password_hash": hash_password("test1234"),
                
                # Basic Personal Information
                "first_name": "Michael",
                "last_name": "Brown",
                "date_of_birth": datetime(1988, 11, 18),
                "phone": "+1777999888",
                
                # Professional Information
                "overall_experience_years": 6,
                "highest_qualification": "Bachelor of Business Administration",
                "previous_organizations": [
                    {
                        "company_name": "StartupHub",
                        "position": "Talent Acquisition Specialist",
                        "duration": "2021-2024",
                        "description": "Specialized in tech talent recruitment"
                    }
                ],
                "skills": ["Talent Acquisition", "Technical Recruiting", "ATS Management", "Candidate Screening"],
                "certifications": [
                    {
                        "name": "Certified Talent Acquisition Professional",
                        "issuer": "Talent Board",
                        "issue_date": datetime(2022, 9, 20),
                        "credential_id": "CTAP-002"
                    }
                ],
                "contributions": "Built talent pipeline of 500+ candidates, improved candidate experience score by 30%",
                "communication_skills": [
                    {"skill": "Candidate Engagement", "level": "expert"},
                    {"skill": "Technical Assessment", "level": "intermediate"}
                ],
                "ai_tools": ["LinkedIn Recruiter", "Greenhouse", "Workable", "ChatGPT"],
                
                # Social Links
                "social_links": {
                    "github": None,
                    "youtube": None,
                    "linkedin": "https://linkedin.com/in/michaelbrown-recruiter",
                    "playstore": None
                },
                
                # Job Application Tracking
                "overall_jobs_applied": [],
                
                # User Classification
                "user_type": "hire",
                "user_status": "active",
                "user_plan": "pro",
                
                # Preferences
                "job_preferences": ["remote", "hybrid"],
                "employment_type": ["full-time"],
                
                # Timestamps
                "profile_created_on": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                
                # Analytics and Metrics
                "match_analysis_count": 35,
                "match_tailored_count": 20,
                "mock_interview_count": 1,
                "profile_completion_count": 88,
                "profile_visits": 32,
                "recent_activity": [
                    {
                        "activity_type": "profile_update",
                        "description": "Updated skills and certifications",
                        "timestamp": datetime.utcnow(),
                        "metadata": {"section": "professional"}
                    }
                ],
                
                # Legacy compatibility
                "username": "hr002",
                "company_name": "InnovateTech",
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": None,
                
                # Legacy structure for backward compatibility
                "personal_info": {
                    "first_name": "Michael",
                    "last_name": "Brown",
                    "phone": "+1777999888",
                    "location": {
                        "city": "Austin",
                        "state": "TX",
                        "country": "USA"
                    }
                },
                "professional_info": {
                    "current_role": "Senior Talent Acquisition Specialist",
                    "current_company": "InnovateTech",
                    "total_experience": "6 years",
                    "industry": "Human Resources",
                    "skills": ["Talent Acquisition", "Technical Recruiting"],
                    "current_salary": 78000,
                    "expected_salary": 88000
                },
                "preferences": {
                    "job_locations": ["Austin", "Remote"],
                    "remote_preference": "remote",
                    "notice_period": "30 days"
                }
            }
        ]
        
        # Insert users into database
        collection = db.database[USERS_COLLECTION]
        
        created_count = 0
        for user_data in test_users:
            try:
                # Check if user already exists
                existing_user = await collection.find_one({"email": user_data["email"]})
                if existing_user:
                    print(f"⚠️ User {user_data['email']} already exists, skipping...")
                    continue
                
                result = await collection.insert_one(user_data)
                created_count += 1
                print(f"✅ Created user: {user_data['email']} (ID: {user_data['user_id']})")
                print(f"   Type: {user_data['user_type']}")
                print(f"   Name: {user_data['first_name']} {user_data['last_name']}")
                print(f"   Experience: {user_data['overall_experience_years']} years")
                print(f"   Skills: {len(user_data['skills'])} skills")
                
            except Exception as e:
                print(f"❌ Failed to create user {user_data['email']}: {e}")
        
        print(f"\n🎉 Created {created_count} test users successfully!")
        
        # Show summary
        total_users = await collection.count_documents({})
        candidates = await collection.count_documents({"user_type": "candidate"})
        hrs = await collection.count_documents({"user_type": "hire"})
        
        print(f"\n📊 Database Summary:")
        print(f"   Total users: {total_users}")
        print(f"   Candidates: {candidates}")
        print(f"   HRs: {hrs}")
        
        return created_count
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        raise e
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_test_users())
