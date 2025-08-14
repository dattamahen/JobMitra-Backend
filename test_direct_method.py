#!/usr/bin/env python3
"""
Direct test of HR dashboard method
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_db import JobDB
from datetime import datetime

async def test_hr_dashboard_direct():
    """Test the HR dashboard method directly"""
    print("🧪 Direct test of get_hr_dashboard method")
    print("=" * 40)
    
    # Create JobDB instance
    job_db = JobDB()
    
    # Test with a fake HR user ID
    test_hr_id = "test_hr_user_123"
    
    try:
        # Call the method directly
        result = await job_db.get_hr_dashboard(test_hr_id)
        
        print("✅ Method executed successfully")
        print(f"📊 Result:")
        print(f"   Total Jobs Posted: {result.total_jobs_posted}")
        print(f"   Active Jobs: {result.active_jobs}")
        print(f"   Inactive Jobs: {result.inactive_jobs}")
        print(f"   Total Applications: {result.total_applications_received}")
        print(f"   Jobs Expiring Soon: {result.jobs_expiring_soon}")
        print(f"   Recent Jobs Count: {len(result.recent_jobs)}")
        
        if result.total_jobs_posted > 0:
            print("\n🎉 SUCCESS: Demo data is working!")
            print("\n📋 Sample Recent Jobs:")
            for i, job in enumerate(result.recent_jobs[:2], 1):
                print(f"   {i}. {job['title']} at {job['company']}")
        else:
            print("\n❌ FAILED: Still returning empty data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hr_dashboard_direct())
