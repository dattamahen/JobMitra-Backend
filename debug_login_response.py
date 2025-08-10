import json
import urllib.request
import urllib.parse

def test_login_debug():
    """Test login and see what user data is returned"""
    
    # Test data for Arjun
    login_data = {
        "email": "arjun.sharma@email.com",
        "password": "TechLead@123"
    }
    
    try:
        print('🔍 Testing login for Arjun Sharma...')
        print(f'Login data: {login_data}')
        
        # Prepare request
        url = "http://localhost:8000/api/v1/auth/login"
        data = json.dumps(login_data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            method='POST'
        )
        
        # Make request
        try:
            with urllib.request.urlopen(req) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                
                print(f'✅ Status code: {status_code}')
                
                if status_code == 200:
                    result = json.loads(response_data)
                    print('✅ Login successful!')
                    print(f'Token: {result.get("access_token", "")[:50]}...')
                    
                    user_data = result.get("user", {})
                    print('👤 User data in login response:')
                    print(f'User ID: {user_data.get("user_id", "Not found")}')
                    print(f'Email: {user_data.get("email", "Not found")}')
                    print(f'First Name: {user_data.get("first_name", "Not found")}')
                    print(f'Last Name: {user_data.get("last_name", "Not found")}')
                    print(f'Full user data: {json.dumps(user_data, indent=2)}')
                    
                    return result
                else:
                    print(f'❌ Unexpected success status: {status_code}')
                    print(f'Response: {response_data}')
                    return None
                    
        except urllib.error.HTTPError as e:
            status_code = e.code
            error_data = e.read().decode('utf-8')
            
            print(f'❌ HTTP Error {status_code}')
            print(f'Error response: {error_data}')
            return None
            
    except Exception as e:
        print(f'❌ Connection error: {e}')
        return None

if __name__ == "__main__":
    test_login_debug()
