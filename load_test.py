"""
Load testing script for JobMitra Backend
Tests production readiness for 10K+ users
"""
import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import List, Dict
import statistics

class LoadTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.errors = []
        
    async def login_user(self, session: aiohttp.ClientSession, user_email: str, password: str) -> str:
        """Login and get JWT token"""
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": user_email, "password": password}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("access_token")
                return None
        except Exception as e:
            self.errors.append(f"Login error: {e}")
            return None
    
    async def test_endpoint(self, session: aiohttp.ClientSession, endpoint: str, 
                           method: str = "GET", token: str = None, data: dict = None) -> Dict:
        """Test a single endpoint"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        start_time = time.time()
        try:
            if method == "GET":
                async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    status = response.status
                    response_time = time.time() - start_time
                    return {"status": status, "response_time": response_time, "endpoint": endpoint}
            elif method == "POST":
                async with session.post(f"{self.base_url}{endpoint}", headers=headers, json=data) as response:
                    status = response.status
                    response_time = time.time() - start_time
                    return {"status": status, "response_time": response_time, "endpoint": endpoint}
        except Exception as e:
            response_time = time.time() - start_time
            self.errors.append(f"Request error for {endpoint}: {e}")
            return {"status": 0, "response_time": response_time, "endpoint": endpoint, "error": str(e)}
    
    async def simulate_user_session(self, session: aiohttp.ClientSession, user_id: int):
        """Simulate a complete user session"""
        # Login
        token = await self.login_user(session, "user001@test.com", "test1234")
        if not token:
            self.errors.append(f"User {user_id} login failed")
            return
        
        # Test various endpoints
        endpoints = [
            ("/api/v1/auth/me", "GET"),
            ("/api/v1/dashboard", "GET"),
            ("/api/v1/users/user001/applied-jobs", "GET"),
            ("/api/v1/jobs", "POST", {"query": "python", "limit": 10}),
            ("/health", "GET"),
        ]
        
        for endpoint_data in endpoints:
            endpoint = endpoint_data[0]
            method = endpoint_data[1]
            data = endpoint_data[2] if len(endpoint_data) > 2 else None
            
            result = await self.test_endpoint(session, endpoint, method, token, data)
            result["user_id"] = user_id
            self.results.append(result)
            
            # Small delay between requests
            await asyncio.sleep(0.1)
    
    async def run_load_test(self, concurrent_users: int = 50, duration_seconds: int = 60):
        """Run load test with specified parameters"""
        print(f"🚀 Starting load test: {concurrent_users} concurrent users for {duration_seconds}s")
        
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            start_time = time.time()
            tasks = []
            
            # Create user simulation tasks
            for user_id in range(concurrent_users):
                task = asyncio.create_task(self.simulate_user_session(session, user_id))
                tasks.append(task)
                
                # Stagger user starts
                if user_id % 10 == 0:
                    await asyncio.sleep(0.5)
            
            # Wait for all tasks to complete or timeout
            try:
                await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=duration_seconds)
            except asyncio.TimeoutError:
                print("⏰ Test timed out - some requests may still be running")
            
            total_time = time.time() - start_time
            print(f"✅ Load test completed in {total_time:.2f}s")
    
    def analyze_results(self):
        """Analyze test results and provide production readiness assessment"""
        if not self.results:
            print("❌ No results to analyze")
            return
        
        # Calculate metrics
        response_times = [r["response_time"] for r in self.results if "error" not in r]
        success_count = len([r for r in self.results if r["status"] == 200])
        error_count = len([r for r in self.results if r["status"] != 200 or "error" in r])
        total_requests = len(self.results)
        
        # Performance metrics
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0
        success_rate = (success_count / total_requests) * 100 if total_requests > 0 else 0
        
        print("\n" + "="*60)
        print("📊 LOAD TEST RESULTS")
        print("="*60)
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {success_count}")
        print(f"Failed Requests: {error_count}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Average Response Time: {avg_response_time:.3f}s")
        print(f"95th Percentile Response Time: {p95_response_time:.3f}s")
        
        # Endpoint breakdown
        endpoint_stats = {}
        for result in self.results:
            endpoint = result["endpoint"]
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"success": 0, "error": 0, "times": []}
            
            if result["status"] == 200:
                endpoint_stats[endpoint]["success"] += 1
            else:
                endpoint_stats[endpoint]["error"] += 1
            
            if "error" not in result:
                endpoint_stats[endpoint]["times"].append(result["response_time"])
        
        print("\n📈 ENDPOINT PERFORMANCE:")
        for endpoint, stats in endpoint_stats.items():
            avg_time = statistics.mean(stats["times"]) if stats["times"] else 0
            success_rate = (stats["success"] / (stats["success"] + stats["error"])) * 100
            print(f"  {endpoint}: {success_rate:.1f}% success, {avg_time:.3f}s avg")
        
        # Production readiness assessment
        print("\n🎯 PRODUCTION READINESS ASSESSMENT:")
        
        if success_rate >= 99:
            print("✅ SUCCESS RATE: Excellent (≥99%)")
        elif success_rate >= 95:
            print("⚠️  SUCCESS RATE: Good (≥95%)")
        else:
            print("❌ SUCCESS RATE: Poor (<95%) - NOT PRODUCTION READY")
        
        if avg_response_time <= 0.5:
            print("✅ RESPONSE TIME: Excellent (≤500ms)")
        elif avg_response_time <= 1.0:
            print("⚠️  RESPONSE TIME: Acceptable (≤1s)")
        else:
            print("❌ RESPONSE TIME: Poor (>1s) - NEEDS OPTIMIZATION")
        
        if p95_response_time <= 2.0:
            print("✅ P95 RESPONSE TIME: Good (≤2s)")
        else:
            print("❌ P95 RESPONSE TIME: Poor (>2s) - NEEDS OPTIMIZATION")
        
        # Error analysis
        if self.errors:
            print(f"\n❌ ERRORS ENCOUNTERED ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
        
        # Final verdict
        print("\n" + "="*60)
        if success_rate >= 95 and avg_response_time <= 1.0 and len(self.errors) < total_requests * 0.05:
            print("🎉 VERDICT: PRODUCTION READY for 10K+ users")
            print("   - High success rate")
            print("   - Acceptable response times")
            print("   - Low error rate")
        else:
            print("⚠️  VERDICT: NEEDS OPTIMIZATION before production")
            print("   - Consider implementing suggested optimizations")
            print("   - Monitor and tune performance")
        print("="*60)

async def main():
    """Run comprehensive load test"""
    tester = LoadTester()
    
    # Test with increasing load
    test_scenarios = [
        (10, 30),   # 10 users for 30s - warm up
        (25, 45),   # 25 users for 45s - moderate load
        (50, 60),   # 50 users for 60s - high load
    ]
    
    for concurrent_users, duration in test_scenarios:
        print(f"\n🔄 Running test scenario: {concurrent_users} users, {duration}s")
        await tester.run_load_test(concurrent_users, duration)
        await asyncio.sleep(5)  # Cool down between tests
    
    tester.analyze_results()

if __name__ == "__main__":
    asyncio.run(main())