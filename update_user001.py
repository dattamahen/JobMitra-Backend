"""
Update user001 with realistic data instead of hardcoded test data
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def update_user001_data():
    """Update user001 with realistic profile data"""
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.jobmitra
        
        # Realistic user data instead of hardcoded test data
        realistic_data = {
            "first_name": "Alex",
            "last_name": "Johnson", 
            "phone": "+91 98765 43210",
            "overall_experience_years": 5,
            "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Python", "AWS", "TypeScript"],
            "profile_completion_count": 85,
            "professional_info": {
                "current_role": "Senior Software Engineer",
                "current_company": "TechCorp Solutions",
                "total_experience": "5 years",
                "industry": "Information Technology",
                "professional_summary": "Experienced full-stack developer with expertise in modern web technologies and cloud platforms",
                "current_salary": 2200000,
                "expected_salary": 2800000,
                "area_of_expertise": ["Web Development", "API Design", "Cloud Architecture"],
                "key_contributions": "Led migration of legacy systems to microservices architecture, improving performance by 40%"
            },
            "personal_info": {
                "location": {
                    "city": "Bangalore",
                    "state": "Karnataka", 
                    "country": "India"
                }
            },
            "certifications": [
                {
                    "name": "AWS Certified Developer",
                    "issuer": "Amazon Web Services",
                    "issue_date": datetime(2023, 6, 15),
                    "credential_id": "AWS-DEV-2023-001"
                }
            ],
            "github_link": "https://github.com/alexjohnson",
            "linkedin_link": "https://linkedin.com/in/alexjohnson-dev",
            "portfolio_url": "https://alexjohnson.dev",
            "updated_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
        
        # Update the user document
        result = await db.users.update_one(
            {"user_id": "user001"},
            {"$set": realistic_data}
        )
        
        print(f"✅ Updated user001: {result.modified_count} document(s) modified")
        
        # Verify the update
        updated_user = await db.users.find_one({"user_id": "user001"})
        if updated_user:
            print("\n📋 Updated user001 profile:")
            print(f"   Name: {updated_user.get('first_name')} {updated_user.get('last_name')}")
            print(f"   Email: {updated_user.get('email')}")
            print(f"   Phone: {updated_user.get('phone')}")
            print(f"   Experience: {updated_user.get('overall_experience_years')} years")
            print(f"   Current Role: {updated_user.get('professional_info', {}).get('current_role')}")
            print(f"   Company: {updated_user.get('professional_info', {}).get('current_company')}")
            print(f"   Skills: {updated_user.get('skills')}")
            print(f"   Profile Completion: {updated_user.get('profile_completion_count')}%")
            print(f"   Location: {updated_user.get('personal_info', {}).get('location', {}).get('city')}")
        
        client.close()
        print("\n🎉 User001 now has realistic data instead of hardcoded test data!")
        
    except Exception as e:
        print(f"❌ Error updating user001: {e}")

if __name__ == "__main__":
    asyncio.run(update_user001_data())
