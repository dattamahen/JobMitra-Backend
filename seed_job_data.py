#!/usr/bin/env python3
"""
Seed Job Data for Kavya Nair (HR User)
Creates 10 different job postings in MongoDB
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_db import JobDB
from job_schemas import JobPostRequest
from auth_db import get_user_by_email

async def create_sample_jobs():
    """Create 10 sample job postings for Kavya Nair"""
    
    print("🏢 Creating Sample Job Postings for Kavya Nair")
    print("=" * 60)
    
    # Get Kavya Nair's user ID
    kavya_user = await get_user_by_email("kavya.nair@email.com")
    if not kavya_user:
        print("❌ Kavya Nair user not found! Please ensure the user exists.")
        return
    
    hr_user_id = kavya_user["user_id"]
    print(f"✅ Found HR User: {kavya_user['name']} (ID: {hr_user_id})")
    
    # Initialize job database
    job_db = JobDB()
    
    # Define 10 different job postings
    sample_jobs = [
        {
            "title": "Senior Full Stack Developer",
            "company": "TechCorp Solutions",
            "location": "San Francisco, CA",
            "employment_type": "full_time",
            "description": """We are seeking a highly skilled Senior Full Stack Developer to join our dynamic engineering team. You will be responsible for developing and maintaining web applications using modern technologies like React, Node.js, and MongoDB.

Key Responsibilities:
• Design and develop scalable web applications
• Collaborate with cross-functional teams
• Mentor junior developers
• Participate in code reviews and technical discussions
• Optimize application performance

What We Offer:
• Competitive salary and equity package
• Comprehensive health benefits
• Flexible work arrangements
• Professional development opportunities
• Modern tech stack and tools""",
            "requirements": [
                "5+ years of experience in full-stack development",
                "Proficiency in React, Node.js, and MongoDB",
                "Experience with REST APIs and GraphQL",
                "Knowledge of cloud platforms (AWS/Azure)",
                "Strong problem-solving skills",
                "Bachelor's degree in Computer Science or related field"
            ],
            "skills": ["React", "Node.js", "MongoDB", "JavaScript", "TypeScript", "AWS", "Docker"],
            "salary_range": {"min": 120000, "max": 160000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=30),
            "is_remote": False,
            "experience_level": "senior"
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudTech Inc",
            "location": "Remote",
            "employment_type": "full_time",
            "description": """Join our DevOps team to help build and maintain scalable infrastructure for our cloud-native applications. You'll work with cutting-edge technologies and help automate our deployment pipelines.

Key Responsibilities:
• Design and implement CI/CD pipelines
• Manage cloud infrastructure on AWS/Azure
• Monitor and optimize system performance
• Implement security best practices
• Collaborate with development teams

What We Offer:
• Remote-first culture
• Competitive compensation
• Learning and development budget
• Latest tools and technologies
• Flexible working hours""",
            "requirements": [
                "3+ years of DevOps experience",
                "Proficiency with Docker and Kubernetes",
                "Experience with AWS or Azure",
                "Knowledge of Infrastructure as Code (Terraform)",
                "Scripting skills (Python, Bash)",
                "Understanding of CI/CD principles"
            ],
            "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Python", "Jenkins", "Monitoring"],
            "salary_range": {"min": 100000, "max": 140000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=25),
            "is_remote": True,
            "experience_level": "mid"
        },
        {
            "title": "Frontend React Developer",
            "company": "StartupXYZ",
            "location": "New York, NY",
            "employment_type": "contract",
            "description": """We're looking for a talented Frontend Developer to join our startup and help build amazing user experiences. You'll work closely with our design team to create responsive and intuitive web applications.

Key Responsibilities:
• Develop responsive web applications using React
• Collaborate with designers and backend developers
• Optimize applications for maximum speed and scalability
• Implement modern frontend best practices
• Participate in agile development processes

What We Offer:
• Competitive contract rates
• Opportunity to work with latest technologies
• Flexible schedule
• Potential for full-time conversion
• Startup equity options""",
            "requirements": [
                "3+ years of React development experience",
                "Strong knowledge of JavaScript/TypeScript",
                "Experience with modern CSS frameworks",
                "Understanding of responsive design principles",
                "Familiarity with testing frameworks (Jest, React Testing Library)",
                "Portfolio showcasing React projects"
            ],
            "skills": ["React", "JavaScript", "TypeScript", "CSS", "HTML", "Redux", "Testing"],
            "salary_range": {"min": 80000, "max": 110000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=18),
            "is_remote": False,
            "experience_level": "mid"
        },
        {
            "title": "Data Scientist",
            "company": "DataFlow Analytics",
            "location": "Boston, MA",
            "employment_type": "full_time",
            "description": """Join our data science team to help extract insights from large datasets and build machine learning models that drive business decisions. You'll work on exciting projects involving predictive analytics and data visualization.

Key Responsibilities:
• Analyze complex datasets to identify trends and patterns
• Build and deploy machine learning models
• Create data visualizations and reports
• Collaborate with business stakeholders
• Present findings to executive leadership

What We Offer:
• Cutting-edge data science tools
• Collaborative research environment
• Conference and training opportunities
• Competitive salary and benefits
• Work-life balance""",
            "requirements": [
                "Master's degree in Data Science, Statistics, or related field",
                "3+ years of experience in data analysis",
                "Proficiency in Python and SQL",
                "Experience with machine learning libraries (scikit-learn, TensorFlow)",
                "Knowledge of statistical analysis and hypothesis testing",
                "Strong communication and presentation skills"
            ],
            "skills": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas", "NumPy", "Visualization"],
            "salary_range": {"min": 110000, "max": 150000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=35),
            "is_remote": False,
            "experience_level": "mid"
        },
        {
            "title": "Mobile App Developer (iOS/Android)",
            "company": "MobileFirst Tech",
            "location": "Austin, TX",
            "employment_type": "full_time",
            "description": """We're seeking a skilled Mobile App Developer to create innovative mobile applications for both iOS and Android platforms. You'll work on consumer-facing apps with millions of users.

Key Responsibilities:
• Develop native mobile applications for iOS and Android
• Collaborate with design and product teams
• Optimize app performance and user experience
• Implement app store best practices
• Stay updated with mobile development trends

What We Offer:
• Work on high-impact consumer apps
• Modern development tools and devices
• Professional growth opportunities
• Flexible work environment
• Comprehensive benefits package""",
            "requirements": [
                "4+ years of mobile app development experience",
                "Proficiency in Swift/Objective-C for iOS or Kotlin/Java for Android",
                "Experience with cross-platform frameworks (React Native/Flutter) is a plus",
                "Understanding of mobile UI/UX principles",
                "Knowledge of app store submission processes",
                "Experience with mobile testing frameworks"
            ],
            "skills": ["iOS Development", "Android Development", "Swift", "Kotlin", "React Native", "Flutter"],
            "salary_range": {"min": 105000, "max": 145000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=28),
            "is_remote": False,
            "experience_level": "senior"
        },
        {
            "title": "Cybersecurity Analyst",
            "company": "SecureNet Solutions",
            "location": "Washington, DC",
            "employment_type": "full_time",
            "description": """Join our cybersecurity team to help protect critical infrastructure and sensitive data. You'll work on threat detection, incident response, and security policy implementation.

Key Responsibilities:
• Monitor security systems for threats and vulnerabilities
• Investigate security incidents and breaches
• Implement security controls and policies
• Conduct security assessments and audits
• Provide security training to staff

What We Offer:
• Work on critical security initiatives
• Security certifications support
• Competitive government contract benefits
• Professional development opportunities
• Clearance sponsorship available""",
            "requirements": [
                "Bachelor's degree in Cybersecurity or related field",
                "2+ years of cybersecurity experience",
                "Knowledge of security frameworks (NIST, ISO 27001)",
                "Experience with SIEM tools and threat detection",
                "Understanding of network security principles",
                "Security certifications (CISSP, CEH, CompTIA Security+) preferred"
            ],
            "skills": ["Cybersecurity", "SIEM", "Incident Response", "Risk Assessment", "Network Security"],
            "salary_range": {"min": 85000, "max": 120000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=40),
            "is_remote": False,
            "experience_level": "mid"
        },
        {
            "title": "Product Manager",
            "company": "InnovateCorp",
            "location": "Seattle, WA",
            "employment_type": "full_time",
            "description": """We're looking for an experienced Product Manager to lead the development of our next-generation SaaS products. You'll work closely with engineering, design, and business teams to deliver products that delight customers.

Key Responsibilities:
• Define product strategy and roadmap
• Gather and prioritize product requirements
• Work closely with engineering teams
• Analyze market trends and customer feedback
• Launch new features and products

What We Offer:
• Lead innovative product initiatives
• Work with cutting-edge technologies
• Collaborative and fast-paced environment
• Equity and stock options
• Professional growth opportunities""",
            "requirements": [
                "5+ years of product management experience",
                "Experience with SaaS products",
                "Strong analytical and problem-solving skills",
                "Excellent communication and leadership abilities",
                "Understanding of agile development methodologies",
                "Bachelor's degree in Business, Engineering, or related field"
            ],
            "skills": ["Product Management", "Strategy", "Analytics", "Agile", "Leadership", "Communication"],
            "salary_range": {"min": 130000, "max": 170000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=32),
            "is_remote": False,
            "experience_level": "senior"
        },
        {
            "title": "Backend Python Developer",
            "company": "APIWorks Inc",
            "location": "Remote",
            "employment_type": "full_time",
            "description": """Join our backend team to build robust and scalable APIs that power our platform. You'll work with Python, Django/FastAPI, and cloud technologies to create high-performance backend systems.

Key Responsibilities:
• Design and develop RESTful APIs
• Optimize database queries and performance
• Implement authentication and authorization systems
• Write comprehensive tests and documentation
• Collaborate with frontend and mobile teams

What We Offer:
• Fully remote position
• Modern Python tech stack
• Flexible working hours
• Learning and development budget
• Health and wellness benefits""",
            "requirements": [
                "4+ years of Python backend development",
                "Experience with Django or FastAPI",
                "Strong knowledge of databases (PostgreSQL, MongoDB)",
                "Understanding of API design principles",
                "Experience with testing frameworks",
                "Knowledge of cloud platforms and deployment"
            ],
            "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "MongoDB", "REST APIs", "Testing"],
            "salary_range": {"min": 95000, "max": 130000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=26),
            "is_remote": True,
            "experience_level": "mid"
        },
        {
            "title": "UX/UI Designer",
            "company": "DesignStudio Pro",
            "location": "Los Angeles, CA",
            "employment_type": "full_time",
            "description": """We're seeking a creative UX/UI Designer to help create intuitive and beautiful user experiences for our digital products. You'll work on web and mobile applications used by thousands of users daily.

Key Responsibilities:
• Create wireframes, prototypes, and high-fidelity designs
• Conduct user research and usability testing
• Collaborate with product and engineering teams
• Maintain design systems and style guides
• Present design concepts to stakeholders

What We Offer:
• Creative and inspiring work environment
• Latest design tools and software
• Portfolio development opportunities
• Collaborative design team
• Competitive salary and benefits""",
            "requirements": [
                "3+ years of UX/UI design experience",
                "Proficiency in design tools (Figma, Sketch, Adobe Creative Suite)",
                "Strong portfolio showcasing web and mobile designs",
                "Understanding of user-centered design principles",
                "Experience with prototyping and user testing",
                "Bachelor's degree in Design or related field"
            ],
            "skills": ["UI Design", "UX Design", "Figma", "Prototyping", "User Research", "Visual Design"],
            "salary_range": {"min": 75000, "max": 105000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=22),
            "is_remote": False,
            "experience_level": "mid"
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Innovations Lab",
            "location": "Palo Alto, CA",
            "employment_type": "full_time",
            "description": """Join our AI team to build and deploy machine learning models at scale. You'll work on cutting-edge ML projects involving computer vision, natural language processing, and recommendation systems.

Key Responsibilities:
• Design and implement ML models and algorithms
• Deploy models to production environments
• Optimize model performance and scalability
• Collaborate with data scientists and engineers
• Research and implement new ML techniques

What We Offer:
• Work on state-of-the-art AI projects
• Access to high-performance computing resources
• Conference attendance and research opportunities
• Competitive compensation and equity
• Collaborative research environment""",
            "requirements": [
                "Master's or PhD in Machine Learning, Computer Science, or related field",
                "4+ years of ML engineering experience",
                "Proficiency in Python and ML frameworks (TensorFlow, PyTorch)",
                "Experience with cloud ML platforms (AWS SageMaker, Google AI Platform)",
                "Strong understanding of ML algorithms and statistics",
                "Experience with MLOps and model deployment"
            ],
            "skills": ["Machine Learning", "Python", "TensorFlow", "PyTorch", "MLOps", "Cloud Platforms"],
            "salary_range": {"min": 140000, "max": 200000, "currency": "USD"},
            "application_deadline": datetime.utcnow() + timedelta(days=45),
            "is_remote": False,
            "experience_level": "senior"
        }
    ]
    
    print(f"\n📝 Creating {len(sample_jobs)} job postings...")
    
    created_jobs = []
    
    for i, job_data in enumerate(sample_jobs, 1):
        try:
            # Create JobPostRequest object
            job_request = JobPostRequest(
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                employment_type=job_data["employment_type"],
                description=job_data["description"],
                requirements=job_data["requirements"],
                skills=job_data["skills"],
                salary_range=job_data["salary_range"],
                application_deadline=job_data["application_deadline"],
                is_remote=job_data["is_remote"],
                experience_level=job_data["experience_level"]
            )
            
            # Create the job in database
            job_id = await job_db.create_job_posting(job_request, hr_user_id)
            
            # Add some realistic application and view counts
            applications_count = random.randint(5, 50)
            views_count = random.randint(50, 300)
            
            # Update the job with some stats
            await job_db.db.database[job_db.jobs_collection].update_one(
                {"_id": job_id},
                {
                    "$set": {
                        "applications_count": applications_count,
                        "views_count": views_count
                    }
                }
            )
            
            created_jobs.append({
                "id": str(job_id),
                "title": job_data["title"],
                "company": job_data["company"],
                "applications": applications_count,
                "views": views_count
            })
            
            print(f"   ✅ {i:2d}. {job_data['title']} at {job_data['company']}")
            print(f"      📊 {applications_count} applications, {views_count} views")
            
        except Exception as e:
            print(f"   ❌ {i:2d}. Failed to create {job_data['title']}: {e}")
    
    print(f"\n🎉 Successfully created {len(created_jobs)} job postings!")
    print(f"📍 All jobs posted by: {kavya_user['name']} ({kavya_user['email']})")
    
    # Display summary
    total_applications = sum(job["applications"] for job in created_jobs)
    total_views = sum(job["views"] for job in created_jobs)
    
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"   Total Jobs Created: {len(created_jobs)}")
    print(f"   Total Applications: {total_applications}")
    print(f"   Total Views: {total_views}")
    print(f"   Average Applications per Job: {total_applications // len(created_jobs) if created_jobs else 0}")
    
    return created_jobs

async def verify_jobs_in_db():
    """Verify the jobs were created in MongoDB"""
    print(f"\n🔍 Verifying jobs in MongoDB...")
    
    # Get Kavya's user ID
    kavya_user = await get_user_by_email("kavya.nair@email.com")
    if not kavya_user:
        print("❌ Cannot verify - Kavya Nair user not found")
        return
    
    hr_user_id = kavya_user["user_id"]
    
    # Query jobs from database
    job_db = JobDB()
    jobs = await job_db.db.database[job_db.jobs_collection].find({
        "posted_by_hr_id": hr_user_id
    }).to_list(None)
    
    print(f"✅ Found {len(jobs)} jobs in MongoDB for {kavya_user['name']}")
    
    for i, job in enumerate(jobs, 1):
        print(f"   {i:2d}. {job['title']} - {job['company']}")
        print(f"      ID: {job['_id']}")
        print(f"      Posted: {job['posted_date']}")
        print(f"      Active: {'Yes' if job.get('is_active', True) else 'No'}")

async def main():
    """Main function to create sample job data"""
    try:
        # Create the jobs
        created_jobs = await create_sample_jobs()
        
        # Verify in database
        await verify_jobs_in_db()
        
        print(f"\n✅ SUCCESS: Job data has been created in MongoDB!")
        print(f"💡 You can now test the HR dashboard API and see real data instead of demo data.")
        print(f"🌐 MongoDB should now contain {len(created_jobs)} job postings by Kavya Nair.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
