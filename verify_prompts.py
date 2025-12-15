#!/usr/bin/env python3
"""
Verify the updated interview prompts in MongoDB
"""

import asyncio
from db_simple import db

async def verify_prompts():
    """Verify the updated prompts in database"""
    try:
        await db.connect_to_mongo()
        
        if db.database is None:
            print("Database connection failed")
            return
        
        print("Connected to database")
        
        # Get all interview prompts
        prompts = await db.database.interview_prompts.find({"prompt_type": "question_generator"}).to_list(None)
        
        print(f"Found {len(prompts)} interview prompts")
        print("=" * 50)
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\nPrompt {i}:")
            print(f"Role Type: {prompt.get('role_type', 'N/A')}")
            print(f"Experience Level: {prompt.get('experience_level', 'N/A')}")
            print(f"Question Count: {prompt.get('question_count', 'N/A')}")
            print(f"Difficulty Distribution: {prompt.get('difficulty_distribution', 'N/A')}")
            
            # Show first 200 characters of prompt
            prompt_text = prompt.get('prompt', '')
            if prompt_text:
                print(f"Prompt Preview: {prompt_text[:200]}...")
            else:
                print("Prompt: Not found")
            print("-" * 30)
        
        print("\nVerification completed!")
        
    except Exception as e:
        print(f"Error verifying prompts: {str(e)}")
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(verify_prompts())