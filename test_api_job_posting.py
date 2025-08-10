"""
Test the job posting API endpoint
"""

import requests
import json
from datetime import datetime


def test_hr_job_posting_api():
    """Test the HR job posting API endpoint"""
    
    # API endpoint
    base_url = "http://localhost:8000"
    
    # Test job data (matching frontend format)
    test_job_data = {
        "title": "Frontend Developer",
        "company": "TechCorp Solutions",
        "location": {
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "is_remote": False,
            "timezone": "IST"
        },
        "employment_type": "full_time",
        "experience_level": "mid",
        "job_type": "onsite",
        "salary": {
            "min": 900000,
            "max": 1400000,
            "currency": "INR",
            "period": "yearly",
            "is_negotiable": True
        },
        "description": "We are looking for a skilled Frontend Developer to join our dynamic team. You will be responsible for building user-facing web applications using modern frameworks and technologies. This is an excellent opportunity to work on cutting-edge projects.",
        "requirements": [
            "3+ years of experience in React.js development",
            "Strong knowledge of JavaScript, HTML5, and CSS3",
            "Experience with state management libraries (Redux/Context)",
            "Understanding of RESTful APIs and integration",
            "Knowledge of version control systems (Git)"
        ],
        "responsibilities": [
            "Develop responsive web applications using React.js",
            "Collaborate with UX/UI designers to implement designs",
            "Optimize applications for maximum speed and scalability",
            "Write clean, maintainable, and well-documented code",
            "Participate in code reviews and team meetings"
        ],
        "skills_required": ["React", "JavaScript", "HTML", "CSS"],
        "skills_preferred": ["TypeScript", "Next.js", "Material-UI"],
        "benefits": ["Health Insurance", "Flexible Working Hours", "Learning Budget", "Remote Work Options"],
        "company_info": {
            "company_size": "51-200",
            "industry": "Information Technology",
            "website": "https://techcorp.com",
            "description": "A leading software development company focused on innovative solutions"
        },
        "hr_contact": {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@techcorp.com",
            "phone": "+91-9876543210",
            "title": "Senior HR Manager",
            "department": "Human Resources"
        },
        "tags": ["frontend", "react", "javascript", "web-development"],
        "application_instructions": "Please submit your resume along with a portfolio of your recent work",
        "external_apply_url": None,
        "application_deadline": None
    }
    
    try:
        # Test without authentication first (should fail)
        print("Testing job posting API...")
        print(f"POST {base_url}/api/v1/hr/jobs")
        
        response = requests.post(
            f"{base_url}/api/v1/hr/jobs",
            json=test_job_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ API correctly requires authentication")
        elif response.status_code == 200 or response.status_code == 201:
            print("✅ Job posted successfully!")
            result = response.json()
            print(f"Job ID: {result.get('job_id', 'N/A')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")


def test_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Backend server is running")
            result = response.json()
            print(f"API: {result.get('message', 'Unknown')}")
            print(f"Version: {result.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        print("Start the backend with: python main.py")
        return False


if __name__ == "__main__":
    print("🔍 Testing JobMitra HR API")
    print("=" * 50)
    
    # Check backend status
    if test_backend_status():
        print("\n" + "-" * 50)
        test_hr_job_posting_api()
    
    print("\n" + "=" * 50)
    print("Test completed")
