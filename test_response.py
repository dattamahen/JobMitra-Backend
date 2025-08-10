import requests
import json

# Login as Kavya
login_data = {'email': 'kavya.nair@email.com', 'password': 'HRUser@12345'}
login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data, verify=False)

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test HR Jobs endpoint
    jobs_response = requests.get('http://localhost:8000/api/v1/hr/jobs', headers=headers, verify=False)
    print(f'Status: {jobs_response.status_code}')
    
    if jobs_response.status_code == 200:
        data = jobs_response.json()
        print('Response structure:')
        print(f'- Type: {type(data)}')
        print(f'- Keys: {list(data.keys()) if isinstance(data, dict) else "Not a dict"}')
        
        if 'jobs' in data:
            print(f'- Jobs count: {len(data["jobs"])}')
            if data['jobs']:
                print(f'- First job keys: {list(data["jobs"][0].keys())}')
        
        print('\nFull response:')
        print(json.dumps(data, indent=2, default=str))
    else:
        print(f'Error: {jobs_response.text}')
else:
    print(f'Login failed: {login_response.status_code}')
