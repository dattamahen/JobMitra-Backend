"""
End-to-end test script for the new user schema
"""

import asyncio
import httpx
import json
from datetime import datetime, date
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.access_token = None
        self.test_user_data = {
            "email": "test.user@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-15",
            "phone": "+1234567890",
            "user_type": "candidate",
            "overall_experience_years": 5,
            "highest_qualification": "Bachelor of Computer Science",
            "skills": ["Python", "JavaScript", "React", "MongoDB"],
            "job_preferences": ["remote", "hybrid"],
            "employment_type": ["full-time"]
        }
    
    async def cleanup_test_user(self):
        """Clean up test user before starting tests"""
        try:
            # This would require admin privileges or direct DB access
            print("🧹 Cleaning up existing test user...")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    async def test_user_registration(self) -> bool:
        """Test user registration with new schema"""
        try:
            print("🧪 Testing user registration...")
            
            response = await self.client.post(
                f"{AUTH_URL}/register",
                json=self.test_user_data
            )
            
            if response.status_code == 201 or response.status_code == 200:
                user_data = response.json()
                print("✅ Registration successful!")
                print(f"   User ID: {user_data.get('user_id')}")
                print(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
                print(f"   User Type: {user_data.get('user_type')}")
                print(f"   Experience: {user_data.get('overall_experience_years')} years")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration test failed: {e}")
            return False
    
    async def test_user_login(self) -> bool:
        """Test user login"""
        try:
            print("🧪 Testing user login...")
            
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            
            response = await self.client.post(
                f"{AUTH_URL}/login",
                json=login_data
            )
            
            if response.status_code == 200:
                login_response = response.json()
                self.access_token = login_response.get("access_token")
                user_data = login_response.get("user", {})
                
                print("✅ Login successful!")
                print(f"   Token received: {bool(self.access_token)}")
                print(f"   User: {user_data.get('first_name')} {user_data.get('last_name')}")
                print(f"   Profile completion: {user_data.get('profile_completion_count', 0)}%")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login test failed: {e}")
            return False
    
    async def test_get_profile(self) -> bool:
        """Test getting user profile"""
        try:
            print("🧪 Testing get user profile...")
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{AUTH_URL}/me",
                headers=headers
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                print("✅ Profile retrieval successful!")
                print(f"   Skills: {profile_data.get('skills', [])}")
                print(f"   Experience: {profile_data.get('overall_experience_years')} years")
                print(f"   Job preferences: {profile_data.get('job_preferences', [])}")
                print(f"   User plan: {profile_data.get('user_plan')}")
                print(f"   Profile visits: {profile_data.get('profile_visits', 0)}")
                return True
            else:
                print(f"❌ Profile retrieval failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Profile test failed: {e}")
            return False
    
    async def test_update_profile(self) -> bool:
        """Test updating user profile"""
        try:
            print("🧪 Testing profile update...")
            
            update_data = {
                "overall_experience_years": 6,
                "skills": ["Python", "JavaScript", "React", "MongoDB", "Docker", "AWS"],
                "certifications": [
                    {
                        "name": "AWS Certified Developer",
                        "issuer": "Amazon Web Services",
                        "issue_date": "2023-01-15",
                        "credential_id": "AWS-DEV-001"
                    }
                ],
                "communication_skills": [
                    {
                        "skill": "Public Speaking",
                        "level": "intermediate"
                    },
                    {
                        "skill": "Technical Writing",
                        "level": "advanced"
                    }
                ],
                "ai_tools": ["ChatGPT", "GitHub Copilot", "Claude"],
                "github_link": "https://github.com/testuser",
                "linkedin_link": "https://linkedin.com/in/testuser",
                "contributions": "Led development of microservices architecture, mentored 3 junior developers",
                "job_preferences": ["remote"],
                "employment_type": ["full-time", "contract"]
            }
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.put(
                f"{AUTH_URL}/profile",
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                updated_profile = response.json()
                print("✅ Profile update successful!")
                print(f"   Updated experience: {updated_profile.get('overall_experience_years')} years")
                print(f"   Updated skills count: {len(updated_profile.get('skills', []))}")
                print(f"   Job preferences: {updated_profile.get('job_preferences', [])}")
                return True
            else:
                print(f"❌ Profile update failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Profile update test failed: {e}")
            return False
    
    async def test_password_change(self) -> bool:
        """Test password change"""
        try:
            print("🧪 Testing password change...")
            
            password_data = {
                "current_password": self.test_user_data["password"],
                "new_password": "newpass123"
            }
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.post(
                f"{AUTH_URL}/change-password",
                json=password_data,
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ Password change successful!")
                
                # Test login with new password
                login_data = {
                    "email": self.test_user_data["email"],
                    "password": "newpass123"
                }
                
                login_response = await self.client.post(
                    f"{AUTH_URL}/login",
                    json=login_data
                )
                
                if login_response.status_code == 200:
                    print("✅ Login with new password successful!")
                    return True
                else:
                    print("❌ Login with new password failed!")
                    return False
            else:
                print(f"❌ Password change failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Password change test failed: {e}")
            return False
    
    async def test_user_analytics_fields(self) -> bool:
        """Test analytics and metrics fields"""
        try:
            print("🧪 Testing analytics fields...")
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{AUTH_URL}/me",
                headers=headers
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Check analytics fields
                analytics_fields = [
                    'match_analysis_count', 'match_tailored_count', 
                    'mock_interview_count', 'profile_completion_count',
                    'profile_visits', 'recent_activity'
                ]
                
                missing_fields = []
                for field in analytics_fields:
                    if field not in profile_data:
                        missing_fields.append(field)
                
                if not missing_fields:
                    print("✅ All analytics fields present!")
                    print(f"   Match analysis count: {profile_data.get('match_analysis_count', 0)}")
                    print(f"   Profile completion: {profile_data.get('profile_completion_count', 0)}%")
                    print(f"   Profile visits: {profile_data.get('profile_visits', 0)}")
                    return True
                else:
                    print(f"❌ Missing analytics fields: {missing_fields}")
                    return False
            else:
                print(f"❌ Analytics test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Analytics test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive API tests for new user schema")
        print("=" * 60)
        
        tests = [
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get Profile", self.test_get_profile),
            ("Update Profile", self.test_update_profile),
            ("Password Change", self.test_password_change),
            ("Analytics Fields", self.test_user_analytics_fields)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            print("-" * 40)
            
            try:
                result = await test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for _, result in results if result)
        total_tests = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! New user schema is working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the errors above.")
        
        await self.client.aclose()
        return passed_tests == total_tests

async def main():
    """Main test runner"""
    tester = APITester()
    
    try:
        await tester.cleanup_test_user()
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 End-to-end testing completed successfully!")
            return 0
        else:
            print("\n❌ End-to-end testing failed!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
