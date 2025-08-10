import json
import urllib.request
import urllib.parse

def test_me_endpoint():
    """Test the /me endpoint to see what user data is returned"""
    
    # You'll need to paste the JWT token here
    token = input("Paste the JWT token from localStorage: ")
    
    try:
        print('🔍 Testing /me endpoint...')
        
        # Prepare request
        url = "http://localhost:8000/api/v1/auth/me"
        
        # Create request with Authorization header
        req = urllib.request.Request(
            url,
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            },
            method='GET'
        )
        
        # Make request
        try:
            with urllib.request.urlopen(req) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                
                print(f'✅ Status code: {status_code}')
                
                if status_code == 200:
                    result = json.loads(response_data)
                    print('📋 User profile from backend:')
                    print(f'User ID: {result.get("user_id", "Not found")}')
                    print(f'Email: {result.get("email", "Not found")}')
                    print(f'First Name: {result.get("first_name", "Not found")}')
                    print(f'Last Name: {result.get("last_name", "Not found")}')
                    print(f'Full response: {json.dumps(result, indent=2)}')
                    return result
                else:
                    print(f'❌ Unexpected status: {status_code}')
                    print(f'Response: {response_data}')
                    return None
                    
        except urllib.error.HTTPError as e:
            status_code = e.code
            error_data = e.read().decode('utf-8')
            
            print(f'❌ HTTP Error {status_code}')
            print(f'Error response: {error_data}')
            return None
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return None

if __name__ == "__main__":
    test_me_endpoint()
