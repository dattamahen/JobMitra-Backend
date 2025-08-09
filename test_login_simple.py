import json
import urllib.request
import urllib.parse

def test_login():
    """Simple test of login endpoint without external dependencies"""
    
    # Test data
    login_data = {
        "email": "arjun.sharma@email.com",
        "password": "TechLead@123"
    }
    
    try:
        print('🔍 Testing login endpoint...')
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
                    print(f'Access token: {result.get("access_token", "")[:50]}...')
                    print(f'User: {result.get("user", {})}')
                    return True
                else:
                    print(f'❌ Unexpected success status: {status_code}')
                    print(f'Response: {response_data}')
                    return False
                    
        except urllib.error.HTTPError as e:
            status_code = e.code
            error_data = e.read().decode('utf-8')
            
            print(f'❌ HTTP Error {status_code}')
            print(f'Error response: {error_data}')
            
            try:
                error_json = json.loads(error_data)
                print(f'Error details: {error_json}')
            except json.JSONDecodeError:
                print('Could not parse error as JSON')
            
            return False
            
    except Exception as e:
        print(f'❌ Connection error: {e}')
        return False

if __name__ == "__main__":
    success = test_login()
    if success:
        print('\n✅ Authentication is working correctly!')
    else:
        print('\n❌ Authentication failed - need to debug further')
