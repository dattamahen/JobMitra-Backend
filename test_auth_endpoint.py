import asyncio
import httpx
import json

async def test_auth_endpoint():
    """Test the authentication endpoint directly"""
    
    try:
        # Test data
        login_data = {
            "email": "arjun.sharma@email.com",
            "password": "TechLead@123"
        }
        
        print('🔍 Testing authentication endpoint...')
        print(f'Login data: {login_data}')
        
        # Test the endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f'Status code: {response.status_code}')
            print(f'Response headers: {dict(response.headers)}')
            
            if response.status_code == 200:
                data = response.json()
                print('✅ Login successful!')
                print(f'Access token: {data.get("access_token", "")[:50]}...')
                print(f'User: {data.get("user", {})}')
            else:
                print('❌ Login failed')
                print(f'Response text: {response.text}')
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    print(f'Error details: {error_data}')
                except:
                    print('Could not parse error response as JSON')
        
    except Exception as e:
        print(f'❌ Error testing endpoint: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth_endpoint())
