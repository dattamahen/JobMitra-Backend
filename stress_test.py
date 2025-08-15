"""
Stress testing script for extreme load scenarios
"""
import asyncio
import aiohttp
import time
import psutil
import os
from datetime import datetime

class StressTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.metrics = {
            "requests_sent": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "total_response_time": 0,
            "max_response_time": 0,
            "min_response_time": float('inf')
        }
    
    async def stress_endpoint(self, session: aiohttp.ClientSession, endpoint: str):
        """Stress test a single endpoint"""
        start_time = time.time()
        try:
            async with session.get(f"{self.base_url}{endpoint}") as response:
                response_time = time.time() - start_time
                self.metrics["requests_sent"] += 1
                self.metrics["total_response_time"] += response_time
                self.metrics["max_response_time"] = max(self.metrics["max_response_time"], response_time)
                self.metrics["min_response_time"] = min(self.metrics["min_response_time"], response_time)
                
                if response.status == 200:
                    self.metrics["requests_successful"] += 1
                else:
                    self.metrics["requests_failed"] += 1
                    
        except Exception as e:
            self.metrics["requests_sent"] += 1
            self.metrics["requests_failed"] += 1
    
    async def run_stress_test(self, requests_per_second: int = 100, duration_seconds: int = 30):
        """Run stress test with specified RPS"""
        print(f"🔥 Stress test: {requests_per_second} RPS for {duration_seconds}s")
        
        connector = aiohttp.TCPConnector(limit=500, limit_per_host=200)
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            start_time = time.time()
            tasks = []
            
            # Monitor system resources
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            while time.time() - start_time < duration_seconds:
                # Create batch of requests
                batch_size = min(requests_per_second, 50)
                for _ in range(batch_size):
                    task = asyncio.create_task(self.stress_endpoint(session, "/health"))
                    tasks.append(task)
                
                # Wait for batch interval
                await asyncio.sleep(1.0 / requests_per_second * batch_size)
                
                # Clean up completed tasks
                if len(tasks) > 1000:
                    done_tasks = [t for t in tasks if t.done()]
                    for task in done_tasks:
                        tasks.remove(task)
            
            # Wait for remaining tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Final system metrics
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"📊 Memory usage: {initial_memory:.1f}MB → {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
    
    def print_results(self):
        """Print stress test results"""
        if self.metrics["requests_sent"] == 0:
            print("❌ No requests completed")
            return
        
        avg_response_time = self.metrics["total_response_time"] / self.metrics["requests_sent"]
        success_rate = (self.metrics["requests_successful"] / self.metrics["requests_sent"]) * 100
        
        print("\n" + "="*50)
        print("🔥 STRESS TEST RESULTS")
        print("="*50)
        print(f"Total Requests: {self.metrics['requests_sent']}")
        print(f"Successful: {self.metrics['requests_successful']}")
        print(f"Failed: {self.metrics['requests_failed']}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Avg Response Time: {avg_response_time:.3f}s")
        print(f"Min Response Time: {self.metrics['min_response_time']:.3f}s")
        print(f"Max Response Time: {self.metrics['max_response_time']:.3f}s")
        
        # Stress test verdict
        if success_rate >= 90 and avg_response_time <= 2.0:
            print("✅ STRESS TEST: PASSED - Can handle high load")
        else:
            print("❌ STRESS TEST: FAILED - Needs optimization")

async def main():
    """Run stress tests"""
    tester = StressTester()
    
    # Progressive stress testing
    stress_levels = [50, 100, 200]  # RPS
    
    for rps in stress_levels:
        print(f"\n🔄 Testing {rps} requests per second...")
        await tester.run_stress_test(rps, 30)
        tester.print_results()
        
        # Reset metrics for next test
        tester.metrics = {
            "requests_sent": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "total_response_time": 0,
            "max_response_time": 0,
            "min_response_time": float('inf')
        }
        
        await asyncio.sleep(10)  # Cool down

if __name__ == "__main__":
    asyncio.run(main())