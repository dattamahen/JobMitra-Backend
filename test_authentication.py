"""
Test authentication for all created test users
"""

import asyncio
import httpx
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"

class AuthTester:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.test_users = [
            {"email": "user001@test.com", "password": "test1234", "type": "candidate", "name": "John Doe"},
            {"email": "user002@test.com", "password": "test1234", "type": "candidate", "name": "Jane Smith"},
            {"email": "hr001@test.com", "password": "test1234", "type": "hire", "name": "Sarah Johnson"},
            {"email": "hr002@test.com", "password": "test1234", "type": "hire", "name": "Michael Brown"}
        ]
    
    async def test_user_login(self, user_data):
        """Test login for a specific user"""
        try:
            print(f"🧪 Testing login for {user_data['name']} ({user_data['email']})...")
            
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = await self.client.post(
                f"{AUTH_URL}/login",
                json=login_data
            )
            
            if response.status_code == 200:
                login_response = response.json()
                token = login_response.get("access_token")
                user_info = login_response.get("user", {})
                
                print(f"✅ Login successful for {user_data['name']}")
                print(f"   User ID: {user_info.get('user_id')}")
                print(f"   User Type: {user_info.get('user_type')}")
                print(f"   Name: {user_info.get('first_name')} {user_info.get('last_name')}")
                print(f"   Experience: {user_info.get('overall_experience_years', 'N/A')} years")
                print(f"   Plan: {user_info.get('user_plan')}")
                print(f"   Token received: {'Yes' if token else 'No'}")
                
                return {"success": True, "token": token, "user": user_info}
            else:
                print(f"❌ Login failed for {user_data['name']}: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Login test failed for {user_data['name']}: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_user_profile(self, user_data, token):
        """Test profile retrieval for a user"""
        try:
            print(f"🔍 Testing profile retrieval for {user_data['name']}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(
                f"{AUTH_URL}/me",
                headers=headers
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                print(f"✅ Profile retrieval successful for {user_data['name']}")
                print(f"   Skills: {len(profile_data.get('skills', []))} skills")
                print(f"   Certifications: {len(profile_data.get('certifications', []))} certifications")
                print(f"   Profile completion: {profile_data.get('profile_completion_count', 0)}%")
                print(f"   Profile visits: {profile_data.get('profile_visits', 0)}")
                print(f"   Match analysis count: {profile_data.get('match_analysis_count', 0)}")
                return {"success": True, "profile": profile_data}
            else:
                print(f"❌ Profile retrieval failed for {user_data['name']}: {response.status_code}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Profile test failed for {user_data['name']}: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_profile_update(self, user_data, token):
        """Test profile update for a user"""
        try:
            print(f"📝 Testing profile update for {user_data['name']}...")
            
            # Different update data based on user type
            if user_data['type'] == 'candidate':
                update_data = {
                    "skills": ["JavaScript", "Python", "React", "Node.js", "TypeScript", "Docker"],
                    "ai_tools": ["GitHub Copilot", "ChatGPT", "Claude", "Cursor"],
                    "job_preferences": ["remote", "hybrid"],
                    "employment_type": ["full-time"]
                }
            else:  # HR
                update_data = {
                    "skills": ["Recruitment", "Talent Acquisition", "HR Analytics", "Employee Relations"],
                    "ai_tools": ["LinkedIn Recruiter", "HiringSolved", "ChatGPT"],
                    "job_preferences": ["hybrid"],
                    "employment_type": ["full-time"]
                }
            
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.put(
                f"{AUTH_URL}/profile",
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                updated_profile = response.json()
                print(f"✅ Profile update successful for {user_data['name']}")
                print(f"   Updated skills: {len(updated_profile.get('skills', []))} skills")
                print(f"   AI tools: {len(updated_profile.get('ai_tools', []))} tools")
                return {"success": True, "updated_profile": updated_profile}
            else:
                print(f"❌ Profile update failed for {user_data['name']}: {response.status_code}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Profile update test failed for {user_data['name']}: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_all_users_authentication(self):
        """Test authentication for all users"""
        print("🚀 Testing Authentication for All Test Users")
        print("=" * 60)
        
        results = []
        
        for user_data in self.test_users:
            print(f"\n{'='*20} {user_data['name']} ({'='*20}")
            
            # Test login
            login_result = await self.test_user_login(user_data)
            
            if login_result["success"]:
                token = login_result["token"]
                
                # Test profile retrieval
                profile_result = await self.test_user_profile(user_data, token)
                
                # Test profile update
                update_result = await self.test_profile_update(user_data, token)
                
                results.append({
                    "user": user_data["name"],
                    "email": user_data["email"],
                    "type": user_data["type"],
                    "login": True,
                    "profile": profile_result["success"],
                    "update": update_result["success"]
                })
            else:
                results.append({
                    "user": user_data["name"],
                    "email": user_data["email"],
                    "type": user_data["type"],
                    "login": False,
                    "profile": False,
                    "update": False
                })
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("=" * 60)
        
        successful_logins = sum(1 for r in results if r["login"])
        successful_profiles = sum(1 for r in results if r["profile"])
        successful_updates = sum(1 for r in results if r["update"])
        total_users = len(results)
        
        print(f"\n🎯 Overall Results:")
        print(f"   Total users tested: {total_users}")
        print(f"   Successful logins: {successful_logins}/{total_users}")
        print(f"   Successful profile retrievals: {successful_profiles}/{total_users}")
        print(f"   Successful profile updates: {successful_updates}/{total_users}")
        
        print(f"\n📋 Individual Results:")
        for result in results:
            login_status = "✅" if result["login"] else "❌"
            profile_status = "✅" if result["profile"] else "❌"
            update_status = "✅" if result["update"] else "❌"
            
            print(f"   {result['user']} ({result['type']}):")
            print(f"      Login: {login_status} | Profile: {profile_status} | Update: {update_status}")
        
        # Check if backend is accessible
        try:
            health_response = await self.client.get(f"{BASE_URL}/health")
            if health_response.status_code == 200:
                print(f"\n✅ Backend server is accessible at {BASE_URL}")
            else:
                print(f"\n⚠️ Backend health check returned {health_response.status_code}")
        except Exception as e:
            print(f"\n❌ Backend server not accessible: {e}")
            print("   Make sure the backend server is running with: python -m uvicorn main:app --reload")
        
        await self.client.aclose()
        
        if successful_logins == total_users and successful_profiles == total_users and successful_updates == total_users:
            print("\n🎉 ALL AUTHENTICATION TESTS PASSED!")
            return True
        else:
            print("\n⚠️ Some authentication tests failed. Check the details above.")
            return False

async def main():
    """Main test runner"""
    tester = AuthTester()
    
    try:
        success = await tester.test_all_users_authentication()
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
