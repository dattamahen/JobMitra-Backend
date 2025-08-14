#!/usr/bin/env python3
"""
Test the Pydantic schema validation directly.
"""

from auth_schemas import UserProfileUpdateRequest
import json

def test_pydantic_validation():
    """Test Pydantic schema validation with problematic payload"""
    
    print("🧪 Testing Pydantic Schema Validation...")
    
    # Original problematic payload from your JSON
    problematic_payload = {
        "first_name": "Alex",
        "last_name": "Johnson", 
        "phone": "+91 98765 43210",
        "city": "Bangalore",
        "current_role": "Senior Software Engineer",
        "current_company": "Updated via Profile",
        "total_experience": "2-3",
        "industry": "Web Development",
        "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Python", "AWS", "TypeScript"],
        "expected_salary": 2500000,
        "professional_summary": "Experienced full-stack developer with expertise in modern web technologies and cloud platforms",
        "desired_job_title": "Stftware Architect", # Typo: "Stftware" -> "Software"
        "certifications": ["[object Object]"], # Invalid: should be Certification objects
        "area_of_expertise": ["Web Development", "API Design", "Cloud Architecture"],
        "key_contributions": "Led migration of legacy systems to microservices architecture, improving performance by 40%",
        "github_url": "https://github.com/user001",
        "portfolio_url": "https://www.test.com",
        "youtube_url": "https://www.youtube.com/@dattamahen"
    }
    
    print("1. Testing original problematic payload...")
    try:
        request = UserProfileUpdateRequest(**problematic_payload)
        print("✅ Original payload validation successful!")
        print(f"Parsed request: {request.dict()}")
    except Exception as e:
        print(f"❌ Original payload validation failed: {e}")
        print(f"Error type: {type(e)}")
    
    # Fixed payload
    fixed_payload = problematic_payload.copy()
    fixed_payload["desired_job_title"] = "Software Architect"  # Fix typo
    # Remove problematic certifications for now
    del fixed_payload["certifications"]
    
    print("\n2. Testing fixed payload...")
    try:
        request = UserProfileUpdateRequest(**fixed_payload)
        print("✅ Fixed payload validation successful!")
        print(f"Parsed skills: {request.skills}")
        print(f"Parsed github_url: {request.github_url}")
        print(f"Parsed expected_salary: {request.expected_salary}")
    except Exception as e:
        print(f"❌ Fixed payload validation failed: {e}")
        print(f"Error type: {type(e)}")
    
    # Test just the certifications issue
    print("\n3. Testing certifications validation...")
    cert_test_payload = {
        "first_name": "Test",
        "certifications": ["[object Object]"]
    }
    
    try:
        request = UserProfileUpdateRequest(**cert_test_payload)
        print("✅ Certifications validation successful!")
        print(f"Parsed certifications: {request.certifications}")
    except Exception as e:
        print(f"❌ Certifications validation failed: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_pydantic_validation()
