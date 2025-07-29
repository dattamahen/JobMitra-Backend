"""
Test MongoDB connectivity
"""
import pymongo
import motor.motor_asyncio
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pymongo_connection():
    """Test basic PyMongo connection"""
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmitra")
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ PyMongo connection successful!")
        
        # Test database access
        db = client.jobmitra
        collection = db.test_collection
        
        # Insert a test document
        result = collection.insert_one({"test": "data", "timestamp": "2025-07-29"})
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Retrieve the document
        doc = collection.find_one({"test": "data"})
        print(f"✅ Test document retrieved: {doc}")
        
        # Clean up
        collection.delete_one({"test": "data"})
        print("✅ Test document cleaned up")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ PyMongo connection failed: {e}")
        return False

async def test_motor_connection():
    """Test Motor (async) connection"""
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmitra")
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Motor (async) connection successful!")
        
        # Test database access
        db = client.jobmitra
        collection = db.test_collection
        
        # Insert a test document
        result = await collection.insert_one({"test": "async_data", "timestamp": "2025-07-29"})
        print(f"✅ Async test document inserted with ID: {result.inserted_id}")
        
        # Retrieve the document
        doc = await collection.find_one({"test": "async_data"})
        print(f"✅ Async test document retrieved: {doc}")
        
        # Clean up
        await collection.delete_one({"test": "async_data"})
        print("✅ Async test document cleaned up")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Motor (async) connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing MongoDB connectivity...")
    print(f"MongoDB URI: {os.getenv('MONGO_URI', 'mongodb://localhost:27017/jobmitra')}")
    print()
    
    # Test PyMongo
    print("1. Testing PyMongo (sync) connection:")
    pymongo_success = test_pymongo_connection()
    print()
    
    # Test Motor
    print("2. Testing Motor (async) connection:")
    motor_success = asyncio.run(test_motor_connection())
    print()
    
    if pymongo_success and motor_success:
        print("🎉 MongoDB is ready for your FastAPI backend!")
    else:
        print("⚠️  MongoDB connection issues detected.")
        print("Please ensure MongoDB is running and accessible.")
