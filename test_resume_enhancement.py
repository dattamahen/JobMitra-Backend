"""
Test script for the resume enhancement functionality.
This script demonstrates how to use the new 3-agent CrewAI workflow.
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test data
TEST_RESUME = """
John Doe
Software Developer
Email: john.doe@email.com
Phone: (555) 123-4567

EXPERIENCE:
Software Developer at TechCorp (2020-2023)
- Developed web applications using Python and JavaScript
- Collaborated with cross-functional teams
- Participated in code reviews

EDUCATION:
Bachelor's in Computer Science, University XYZ (2016-2020)

SKILLS:
Python, JavaScript, HTML, CSS, Git
"""

TEST_JOB_DESCRIPTION = """
Senior Full Stack Developer

We are looking for an experienced Senior Full Stack Developer to join our dynamic team.

REQUIREMENTS:
- 5+ years of experience in full-stack web development
- Strong proficiency in Python, JavaScript, React, Node.js
- Experience with databases (PostgreSQL, MongoDB)
- Knowledge of cloud platforms (AWS, Azure, GCP)
- Experience with containerization (Docker, Kubernetes)
- Familiarity with DevOps practices and CI/CD pipelines
- Strong problem-solving and communication skills
- Bachelor's degree in Computer Science or related field

RESPONSIBILITIES:
- Design and develop scalable web applications
- Collaborate with product managers and designers
- Implement best practices for code quality and testing
- Mentor junior developers
- Participate in architectural decisions
"""

async def test_resume_enhancement():
    """Test the resume enhancement functionality."""
    try:
        # Import the function (this will test if all imports work)
        from crew_agent import run_resume_enhancement_crew
        
        print("="*60)
        print("TESTING RESUME ENHANCEMENT WORKFLOW")
        print("="*60)
        print(f"Original Resume Length: {len(TEST_RESUME)} characters")
        print(f"Job Description Length: {len(TEST_JOB_DESCRIPTION)} characters")
        print("\n" + "-"*40)
        print("Starting 3-agent workflow...")
        print("-"*40)
        
        # Test the resume enhancement
        enhanced_resume = run_resume_enhancement_crew(TEST_RESUME, TEST_JOB_DESCRIPTION)
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(f"Enhanced Resume Length: {len(enhanced_resume)} characters")
        print(f"Length Increase: {len(enhanced_resume) - len(TEST_RESUME)} characters")
        
        print("\n" + "-"*40)
        print("ORIGINAL RESUME (first 300 chars):")
        print("-"*40)
        print(TEST_RESUME[:300] + "...")
        
        print("\n" + "-"*40)
        print("ENHANCED RESUME (first 500 chars):")
        print("-"*40)
        print(enhanced_resume[:500] + "...")
        
        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        return enhanced_resume
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure all required packages are installed:")
        print("pip install crewai langchain-openai motor pymongo fastapi")
        return None
        
    except Exception as e:
        print(f"Test Error: {e}")
        print("Make sure your OPENAI_API_KEY is set in the .env file")
        return None

async def test_basic_functionality():
    """Test basic CrewAI functionality."""
    try:
        from crew_agent import run_crew_ai
        
        print("="*60)
        print("TESTING BASIC CREWAI FUNCTIONALITY")
        print("="*60)
        
        test_query = "What are the key skills for a full-stack developer?"
        print(f"Test Query: {test_query}")
        
        response = run_crew_ai(test_query)
        
        print("\n" + "-"*40)
        print("AI Response:")
        print("-"*40)
        print(response[:500] + "..." if len(response) > 500 else response)
        
        print("\n" + "="*60)
        print("BASIC TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        return response
        
    except Exception as e:
        print(f"Basic Test Error: {e}")
        return None

async def main():
    """Run all tests."""
    print("Starting JobMitra Backend Tests...")
    print("Make sure your .env file has OPENAI_API_KEY set!")
    print("\n")
    
    # Test basic functionality first
    basic_result = await test_basic_functionality()
    
    if basic_result:
        print("\n\n")
        # Test resume enhancement
        resume_result = await test_resume_enhancement()
        
        if resume_result:
            print("\n" + "="*60)
            print("ALL TESTS PASSED! 🎉")
            print("="*60)
            print("Your JobMitra backend is ready for:")
            print("1. Basic query processing (/ask endpoint)")
            print("2. Resume enhancement (/resume-enhance endpoint)")
            print("3. MongoDB logging for both features")
        else:
            print("\n" + "="*60)
            print("RESUME ENHANCEMENT TEST FAILED ❌")
            print("="*60)
    else:
        print("\n" + "="*60)
        print("BASIC FUNCTIONALITY TEST FAILED ❌")
        print("="*60)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
