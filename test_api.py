"""
Comprehensive test script for JobMitra Backend API.
Tests all endpoints and features to verify functionality.
"""

import asyncio
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


BASE_URL = "http://localhost:8000"
API_BASE_URL = f"{BASE_URL}/api/v1"


def test_api_health():
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Health check endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Health check error: {e}")


def test_extended_health():
    """Test the extended health check endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Extended health check endpoint working")
            result = response.json()
            print(f"API Version: {result.get('api_version')}")
            print(f"Features: {', '.join(result.get('features', []))}")
        else:
            print(f"❌ Extended health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Extended health check error: {e}")


def test_ask_endpoint():
    """Test the /ask endpoint."""
    try:
        test_query = {
            "query": "What are the key benefits of using Python for web development?"
        }
        
        response = requests.post(
            f"{BASE_URL}/ask",
            headers={"Content-Type": "application/json"},
            json=test_query
        )
        
        if response.status_code == 200:
            print("✅ /ask endpoint working")
            result = response.json()
            print(f"Query: {test_query['query']}")
            print(f"Response: {result['response'][:100]}...")
            print(f"Timestamp: {result['timestamp']}")
        else:
            print(f"❌ /ask endpoint failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ /ask endpoint error: {e}")


def test_user_management():
    """Test user management endpoints."""
    try:
        # Test user creation
        user_data = {
            "user_id": "test_user_123",
            "email": "testuser@example.com",
            "full_name": "Test User",
            "phone": "+1 (555) 999-0000",
            "current_job_title": "Software Developer",
            "skills": ["Python", "FastAPI", "MongoDB"]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/users",
            headers={"Content-Type": "application/json"},
            json=user_data
        )
        
        if response.status_code == 200:
            print("✅ User creation endpoint working")
            result = response.json()
            print(f"Created user: {result['user_id']}")
            
            # Test user retrieval
            user_id = user_data["user_id"]
            get_response = requests.get(f"{API_BASE_URL}/users/{user_id}")
            
            if get_response.status_code == 200:
                print("✅ User retrieval endpoint working")
                user_profile = get_response.json()
                print(f"Retrieved user: {user_profile['full_name']}")
            else:
                print(f"❌ User retrieval failed: {get_response.status_code}")
                
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ User management error: {e}")


def test_job_search():
    """Test job search endpoint."""
    try:
        search_request = {
            "query": "python developer",
            "skills": ["Python", "Django"],
            "location_type": "remote",
            "limit": 5
        }
        
        response = requests.post(
            f"{API_BASE_URL}/jobs/search",
            headers={"Content-Type": "application/json"},
            json=search_request
        )
        
        if response.status_code == 200:
            print("✅ Job search endpoint working")
            result = response.json()
            print(f"Found {result['count']} jobs")
            if result['jobs']:
                first_job = result['jobs'][0]
                print(f"Sample job: {first_job.get('title', 'N/A')}")
        else:
            print(f"❌ Job search failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Job search error: {e}")


def test_learning_resources():
    """Test learning resources endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/learning-resources?skill=Python&limit=3")
        
        if response.status_code == 200:
            print("✅ Learning resources endpoint working")
            result = response.json()
            print(f"Found {result['count']} Python learning resources")
            if result['resources']:
                first_resource = result['resources'][0]
                print(f"Sample resource: {first_resource.get('title', 'N/A')}")
        else:
            print(f"❌ Learning resources failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Learning resources error: {e}")


def test_mock_interview():
    """Test mock interview endpoints."""
    try:
        interview_data = {
            "user_id": "test_user_123",
            "skill": "Python",
            "difficulty_level": "intermediate"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/mock-interviews",
            headers={"Content-Type": "application/json"},
            json=interview_data
        )
        
        if response.status_code == 200:
            print("✅ Mock interview creation endpoint working")
            result = response.json()
            print(f"Created interview session: {result['session_id']}")
        else:
            print(f"❌ Mock interview creation failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Mock interview error: {e}")


def test_dashboard():
    """Test dashboard endpoint."""
    try:
        user_id = "test_user_123"
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/dashboard")
        
        if response.status_code == 200:
            print("✅ Dashboard endpoint working")
            result = response.json()
            print(f"Dashboard data for user: {user_id}")
            print(f"Profile completion: {result.get('profile_completion', 0)}%")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")


def test_logs_endpoint():
    """Test the /logs endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/logs?limit=5")
        
        if response.status_code == 200:
            print("✅ /logs endpoint working")
            result = response.json()
            print(f"Found {result['count']} log entries")
        else:
            print(f"❌ /logs endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ /logs endpoint error: {e}")


def test_analytics():
    """Test analytics endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/summary")
        
        if response.status_code == 200:
            print("✅ Analytics endpoint working")
            result = response.json()
            print(f"Analytics summary: {result}")
        else:
            print(f"❌ Analytics failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Analytics error: {e}")


def run_comprehensive_tests():
    """Run all API tests in sequence."""
    print("Testing JobMitra Backend API - Comprehensive Test Suite")
    print("=" * 60)
    
    print("\n1. Testing Core Health Endpoints:")
    test_api_health()
    test_extended_health()
    
    print("\n2. Testing AI Query Endpoint:")
    test_ask_endpoint()
    
    print("\n3. Testing User Management:")
    test_user_management()
    
    print("\n4. Testing Job Search:")
    test_job_search()
    
    print("\n5. Testing Learning Resources:")
    test_learning_resources()
    
    print("\n6. Testing Mock Interview System:")
    test_mock_interview()
    
    print("\n7. Testing Dashboard:")
    test_dashboard()
    
    print("\n8. Testing Logs:")
    test_logs_endpoint()
    
    print("\n9. Testing Analytics:")
    test_analytics()
    
    print("\n" + "=" * 60)
    print("Comprehensive testing completed!")
    print("\nNext Steps:")
    print("1. Check API documentation: http://localhost:8000/docs")
    print("2. Seed sample data: python seed_data.py")
    print("3. Monitor logs for any issues")
    print("4. Test with real user scenarios")


if __name__ == "__main__":
    run_comprehensive_tests()
