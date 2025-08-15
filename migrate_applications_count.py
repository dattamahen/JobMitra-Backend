"""
Migration script to convert applications_count from int to array
"""

import asyncio
from db_simple import db

async def migrate_applications_count():
    """Convert all integer applications_count fields to empty arrays"""
    try:
        await db.connect_to_mongo()
        
        # Update all jobs where applications_count is a number
        result = await db.database["jobs"].update_many(
            {"applications_count": {"$type": "number"}},
            {"$set": {"applications_count": []}}
        )
        
        print(f"Migrated {result.modified_count} jobs from int to array format")
        
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(migrate_applications_count())