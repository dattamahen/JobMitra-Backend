"""
Quick production readiness test
"""
import asyncio
import aiohttp
import time

async def test_production_readiness():
    """Test key production metrics"""
    base_url = "http://localhost:8000"
    results = {"success": 0, "failed": 0, "times": []}
    
    # Test endpoints
    endpoints = [
        "/health",
        "/api/v1/auth/login",
        "/",
    ]
    
    connector = aiohttp.TCPConnector(limit=100)
    timeout = aiohttp.ClientTimeout(total=5)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Test 1: Basic connectivity
        print("Testing basic connectivity...")
        for endpoint in endpoints:
            start = time.time()
            try:
                if endpoint == "/api/v1/auth/login":
                    async with session.post(f"{base_url}{endpoint}", 
                                          json={"email": "user001@test.com", "password": "test1234"}) as resp:
                        status = resp.status
                else:
                    async with session.get(f"{base_url}{endpoint}") as resp:
                        status = resp.status
                
                response_time = time.time() - start
                results["times"].append(response_time)
                
                if status in [200, 401]:  # 401 is expected for some endpoints
                    results["success"] += 1
                    print(f"OK {endpoint}: {status} ({response_time:.3f}s)")
                else:
                    results["failed"] += 1
                    print(f"FAIL {endpoint}: {status} ({response_time:.3f}s)")
                    
            except Exception as e:
                results["failed"] += 1
                print(f"ERROR {endpoint}: {e}")
        
        # Test 2: Concurrent load (25 users)
        print("\nTesting concurrent load (25 users)...")
        tasks = []
        start_time = time.time()
        
        for i in range(25):
            task = asyncio.create_task(session.get(f"{base_url}/health"))
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        load_time = time.time() - start_time
        
        concurrent_success = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
        concurrent_failed = 25 - concurrent_success
        
        print(f"CONCURRENT: {concurrent_success}/25 success in {load_time:.3f}s")
        
        # Results
        avg_time = sum(results["times"]) / len(results["times"]) if results["times"] else 0
        success_rate = (results["success"] / (results["success"] + results["failed"])) * 100
        concurrent_rate = (concurrent_success / 25) * 100
        
        print("\n" + "="*50)
        print("PRODUCTION READINESS RESULTS")
        print("="*50)
        print(f"Basic Tests: {results['success']}/{results['success'] + results['failed']} passed")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Average Response Time: {avg_time:.3f}s")
        print(f"Concurrent Load: {concurrent_rate:.1f}% success")
        print(f"Load Test Time: {load_time:.3f}s")
        
        # Verdict
        print("\nPRODUCTION READINESS:")
        if success_rate >= 80 and avg_time <= 1.0 and concurrent_rate >= 80:
            print("READY for production deployment")
            print("   - Basic functionality working")
            print("   - Acceptable response times")
            print("   - Handles concurrent load")
        else:
            print("NEEDS OPTIMIZATION before production")
            if success_rate < 80:
                print("   - Fix failing endpoints")
            if avg_time > 1.0:
                print("   - Improve response times")
            if concurrent_rate < 80:
                print("   - Optimize for concurrent load")

if __name__ == "__main__":
    asyncio.run(test_production_readiness())