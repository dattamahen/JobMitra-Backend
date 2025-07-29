"""
Database seeding script for JobMitra Backend.
Populates the database with sample data for development and testing.
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from db import db, COLLECTION_NAMES
from schemas import (
    UserProfile, JobListing, LearningResource,
    CompanyInfo, SalaryRange, Location, SocialLinks,
    JobRequirement, JobBenefit, HRContact
)


async def seed_sample_data():
    """Seed the database with sample data."""
    
    print("Starting database seeding...")
    
    # Connect to database
    await db.connect_to_mongo()
    
    # Sample Companies
    companies = [
        CompanyInfo(
            id="techcorp",
            name="TechCorp Inc.",
            industry="Technology",
            size="1000-5000",
            website="https://techcorp.com",
            description="Leading technology solutions provider"
        ),
        CompanyInfo(
            id="innovateai",
            name="InnovateAI",
            industry="Artificial Intelligence",
            size="500-1000",
            website="https://innovateai.com",
            description="AI-powered recruitment and HR solutions"
        ),
        CompanyInfo(
            id="dataflow",
            name="DataFlow Solutions",
            industry="Data Analytics",
            size="100-500",
            website="https://dataflow.com",
            description="Advanced data analytics and machine learning platform"
        )
    ]
    
    # Sample Job Requirements
    requirements = [
        JobRequirement(
            id="req-1",
            description="5+ years of experience in software development",
            type="required",
            category="experience"
        ),
        JobRequirement(
            id="req-2",
            description="Proficiency in JavaScript, Python, or Java",
            type="required",
            category="technical"
        ),
        JobRequirement(
            id="req-3",
            description="Experience with React and Node.js",
            type="required",
            category="technical"
        ),
        JobRequirement(
            id="req-4",
            description="Knowledge of cloud platforms (AWS, GCP, or Azure)",
            type="preferred",
            category="technical"
        )
    ]
    
    # Sample Job Benefits
    benefits = [
        JobBenefit(
            id="benefit-1",
            title="Health Insurance",
            description="Comprehensive medical, dental, and vision coverage",
            category="health"
        ),
        JobBenefit(
            id="benefit-2",
            title="401(k) Matching",
            description="Company matches up to 6% of salary",
            category="financial"
        ),
        JobBenefit(
            id="benefit-3",
            title="Flexible PTO",
            description="Unlimited paid time off policy",
            category="time-off"
        ),
        JobBenefit(
            id="benefit-4",
            title="Learning Budget",
            description="$2000 annual professional development budget",
            category="professional"
        )
    ]
    
    # Sample HR Contact
    hr_contact = HRContact(
        name="Sarah Johnson",
        email="sarah.johnson@techcorp.com",
        phone="+1 (555) 123-4567",
        title="Senior Technical Recruiter",
        department="Human Resources"
    )
    
    # Sample Job Listings
    job_listings = [
        JobListing(
            job_id="senior-software-engineer",
            title="Senior Software Engineer",
            company=companies[0],
            location=Location(
                type="hybrid",
                city="San Francisco",
                state="CA",
                country="USA",
                timezone="PST"
            ),
            salary=SalaryRange(
                min=120000,
                max=180000,
                currency="USD",
                period="yearly"
            ),
            description="We are looking for a Senior Software Engineer to join our dynamic team and help build next-generation AI-powered applications. You will be responsible for designing, developing, and maintaining scalable web applications using modern technologies.",
            short_description="Join our team to build scalable AI-powered applications...",
            requirements=requirements,
            benefits=benefits,
            hr_contact=hr_contact,
            skills=["JavaScript", "React", "Node.js", "Python", "AWS", "Docker", "Kubernetes"],
            experience_level="senior",
            employment_type="full-time",
            department="Engineering",
            posted_date=datetime.utcnow(),
            application_deadline=datetime.utcnow() + timedelta(days=30),
            is_active=True,
            tags=["ai", "full-stack", "cloud", "remote-friendly"]
        ),
        JobListing(
            job_id="product-manager",
            title="Product Manager",
            company=companies[1],
            location=Location(
                type="onsite",
                city="New York",
                state="NY",
                country="USA",
                timezone="EST"
            ),
            salary=SalaryRange(
                min=100000,
                max=150000,
                currency="USD",
                period="yearly"
            ),
            description="We are seeking an experienced Product Manager to lead the product strategy and roadmap for our AI-powered recruitment platform.",
            short_description="Lead product strategy for our AI recruitment platform...",
            requirements=requirements[2:],  # Different requirements
            benefits=benefits,
            hr_contact=HRContact(
                name="Michael Chen",
                email="michael.chen@innovateai.com",
                phone="+1 (555) 234-5678",
                title="Talent Acquisition Manager",
                department="Human Resources"
            ),
            skills=["Product Management", "Analytics", "SaaS", "Agile", "User Research", "SQL"],
            experience_level="mid",
            employment_type="full-time",
            department="Product",
            posted_date=datetime.utcnow() - timedelta(days=5),
            application_deadline=datetime.utcnow() + timedelta(days=25),
            is_active=True,
            tags=["product", "saas", "ai", "hr-tech"]
        ),
        JobListing(
            job_id="data-scientist",
            title="Data Scientist",
            company=companies[2],
            location=Location(
                type="remote",
                country="USA",
                timezone="Various"
            ),
            salary=SalaryRange(
                min=130000,
                max=170000,
                currency="USD",
                period="yearly"
            ),
            description="Join our data science team to develop and implement machine learning models that power our talent matching algorithms.",
            short_description="Develop machine learning models for talent matching...",
            requirements=requirements,
            benefits=benefits,
            hr_contact=HRContact(
                name="Emily Rodriguez",
                email="emily.rodriguez@dataflow.com",
                phone="+1 (555) 345-6789",
                title="HR Business Partner",
                department="Human Resources"
            ),
            skills=["Python", "Machine Learning", "TensorFlow", "PyTorch", "SQL", "Statistics", "AWS"],
            experience_level="mid",
            employment_type="full-time",
            department="Data Science",
            posted_date=datetime.utcnow() - timedelta(days=2),
            application_deadline=datetime.utcnow() + timedelta(days=28),
            is_active=True,
            tags=["data-science", "machine-learning", "remote", "analytics"]
        )
    ]
    
    # Sample Learning Resources
    learning_resources = [
        LearningResource(
            resource_id="js-1",
            title="JavaScript Crash Course For Beginners",
            description="Learn JavaScript fundamentals including variables, functions, DOM manipulation, and more",
            url="https://www.youtube.com/watch?v=hdI2bqOjy3c",
            resource_type="video",
            skill="JavaScript",
            level="beginner",
            duration_minutes=100,
            provider="Traversy Media",
            rating=4.8,
            tags=["javascript", "programming", "web-development"]
        ),
        LearningResource(
            resource_id="react-1",
            title="React Tutorial for Beginners",
            description="Complete React tutorial covering components, state, props, and hooks",
            url="https://www.youtube.com/watch?v=bMknfKXIFA8",
            resource_type="video",
            skill="React",
            level="beginner",
            duration_minutes=228,
            provider="React",
            rating=4.9,
            tags=["react", "javascript", "frontend", "web-development"]
        ),
        LearningResource(
            resource_id="python-1",
            title="Python Tutorial - Python for Beginners",
            description="Complete Python tutorial covering syntax, data structures, functions, and OOP",
            url="https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            resource_type="video",
            skill="Python",
            level="beginner",
            duration_minutes=374,
            provider="Programming with Mosh",
            rating=4.9,
            tags=["python", "programming", "data-science"]
        ),
        LearningResource(
            resource_id="ml-1",
            title="Machine Learning Course for Beginners",
            description="Introduction to ML concepts, algorithms, and hands-on projects with Python",
            url="https://www.youtube.com/watch?v=NWONeJKn6kc",
            resource_type="video",
            skill="Machine Learning",
            level="beginner",
            duration_minutes=652,
            provider="FreeCodeCamp",
            rating=4.8,
            tags=["machine-learning", "python", "data-science", "ai"]
        ),
        LearningResource(
            resource_id="aws-1",
            title="AWS Tutorial for Beginners",
            description="Introduction to AWS services including EC2, S3, RDS, and basic cloud concepts",
            url="https://www.youtube.com/watch?v=3hLmDS179YE",
            resource_type="video",
            skill="AWS",
            level="beginner",
            duration_minutes=269,
            provider="FreeCodeCamp",
            rating=4.8,
            tags=["aws", "cloud", "devops", "infrastructure"]
        )
    ]
    
    # Sample User Profiles
    user_profiles = [
        UserProfile(
            user_id="user_001",
            email="john.doe@example.com",
            full_name="John Doe",
            phone="+1 (555) 100-0001",
            location=Location(
                city="San Francisco",
                state="CA",
                country="USA",
                type="hybrid"
            ),
            current_job_title="Software Engineer",
            desired_job_title="Senior Software Engineer",
            experience_years="4-5",
            skills=["JavaScript", "React", "Node.js", "Python", "SQL"],
            certifications=["AWS Certified Developer"],
            area_of_expertise=["Frontend Development", "Full Stack Development"],
            professional_summary="Experienced software engineer with 4+ years in full-stack development",
            social_links=SocialLinks(
                github="https://github.com/johndoe",
                portfolio="https://johndoe.dev"
            ),
            profile_completion_percentage=85,
            is_active=True
        ),
        UserProfile(
            user_id="user_002",
            email="jane.smith@example.com",
            full_name="Jane Smith",
            phone="+1 (555) 100-0002",
            location=Location(
                city="New York",
                state="NY",
                country="USA",
                type="onsite"
            ),
            current_job_title="Data Analyst",
            desired_job_title="Data Scientist",
            experience_years="2-3",
            skills=["Python", "SQL", "Machine Learning", "Statistics", "Pandas"],
            certifications=["Google Data Analytics Certificate"],
            area_of_expertise=["Data Analysis", "Machine Learning"],
            professional_summary="Data analyst transitioning to data science with strong analytical skills",
            social_links=SocialLinks(
                github="https://github.com/janesmith",
                linkedin="https://linkedin.com/in/janesmith"
            ),
            profile_completion_percentage=90,
            is_active=True
        )
    ]
    
    # Insert data into collections
    try:
        # Insert Job Listings
        jobs_collection = db.database[COLLECTION_NAMES["jobs"]]
        jobs_data = [job.dict(by_alias=True, exclude_unset=True) for job in job_listings]
        await jobs_collection.insert_many(jobs_data)
        print(f"Inserted {len(job_listings)} job listings")
        
        # Insert Learning Resources
        resources_collection = db.database[COLLECTION_NAMES["learning_resources"]]
        resources_data = [resource.dict(by_alias=True, exclude_unset=True) for resource in learning_resources]
        await resources_collection.insert_many(resources_data)
        print(f"Inserted {len(learning_resources)} learning resources")
        
        # Insert User Profiles
        users_collection = db.database[COLLECTION_NAMES["users"]]
        users_data = [user.dict(by_alias=True, exclude_unset=True) for user in user_profiles]
        await users_collection.insert_many(users_data)
        print(f"Inserted {len(user_profiles)} user profiles")
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
    
    finally:
        # Close database connection
        await db.close_mongo_connection()


async def clear_collections():
    """Clear all collections (use with caution!)."""
    print("WARNING: This will clear all data!")
    confirm = input("Type 'YES' to confirm: ")
    
    if confirm != "YES":
        print("Operation cancelled")
        return
    
    await db.connect_to_mongo()
    
    try:
        for collection_name in COLLECTION_NAMES.values():
            collection = db.database[collection_name]
            result = await collection.delete_many({})
            print(f"Cleared {result.deleted_count} documents from {collection_name}")
        
        print("All collections cleared!")
        
    except Exception as e:
        print(f"Error clearing collections: {e}")
    
    finally:
        await db.close_mongo_connection()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        # Clear data
        asyncio.run(clear_collections())
    else:
        # Seed data
        asyncio.run(seed_sample_data())
