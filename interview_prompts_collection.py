from pymongo import MongoClient
from datetime import datetime

def get_mock_interview_prompt_template():
    """
    Updated mock interview question generation prompt template
    """
    return """
Generate mock interview questions using the following inputs:

Role: {{ROLE}}
Primary Skills: {{SKILLS}}
Total Experience: {{TOTAL_EXPERIENCE}} years

Requirements:
- Generate 15–20 questions
- Progressive difficulty (Easy -> Medium -> Hard)
- Difficulty distribution:
  - Easy: 30%
  - Medium: 40%
  - Hard: 30%
- Match question depth to experience level
- Include conceptual, practical, and scenario-based questions
- Avoid trick or puzzle questions

For each question include:
- Question number
- Clear, real-world phrasing

Output format:
1. What is the difference between a list and a tuple in Python?
2. How would you implement caching in a REST API?
3. Design a scalable microservices architecture for an e-commerce platform.

IMPORTANT: Generate ONLY the numbered questions. Do NOT include any introductory text, explanations, or additional commentary. Start directly with question 1.
"""

# MongoDB Collection Schema for Interview Prompts
def create_interview_prompts_collection():
    """
    Collection: interview_prompts
    
    Document Structure:
    {
        "_id": ObjectId,
        "role": "software_engineer",
        "experience_level": "junior",  # junior, mid, senior
        "technology": "python",
        "prompt_template": "Updated structured prompt template",
        "question_count": 18,
        "difficulty_distribution": {"easy": 30, "medium": 40, "hard": 30},
        "created_at": datetime,
        "updated_at": datetime
    }
    """
    
    base_template = get_mock_interview_prompt_template()
    
    # Sample prompts for different combinations
    sample_prompts = [
        {
            "role": "software_engineer",
            "experience_level": "junior",
            "technology": "python",
            "prompt_template": base_template,
            "question_count": 18,
            "difficulty_distribution": {"easy": 30, "medium": 40, "hard": 30},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "software_engineer", 
            "experience_level": "mid",
            "technology": "python",
            "prompt_template": base_template,
            "question_count": 18,
            "difficulty_distribution": {"easy": 30, "medium": 40, "hard": 30},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "software_engineer",
            "experience_level": "senior", 
            "technology": "python",
            "prompt_template": base_template,
            "question_count": 18,
            "difficulty_distribution": {"easy": 30, "medium": 40, "hard": 30},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "data_scientist",
            "experience_level": "junior",
            "technology": "python",
            "prompt_template": base_template,
            "question_count": 18,
            "difficulty_distribution": {"easy": 30, "medium": 40, "hard": 30},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "frontend_developer",
            "experience_level": "mid",
            "technology": "javascript",
            "prompt_template": base_template,
            "question_count": 18,
            "difficulty_distribution": {"easy": 30, "medium": 40, "hard": 30},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    return sample_prompts

def get_smart_prompt(user_profile):
    """
    Smart prompt selection based on user profile
    """
    experience = user_profile.get('experience_years', 0)
    skills = user_profile.get('skills', [])
    
    # Determine role_type based on skills
    tech_skills = ['python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 'mongodb', 'aws', 'docker', 'kubernetes', 'typescript']
    is_technical = any(skill.lower() in tech_skills for skill in skills)
    role_type = 'technical' if is_technical else 'general'
    
    # Map experience to levels matching database schema
    if experience <= 1:
        experience_level = '0-1'
    elif experience <= 3:
        experience_level = '1-3'
    elif experience <= 7:
        experience_level = '3-7'
    else:
        experience_level = '7+'
    
    return {'experience_level': experience_level, 'role_type': role_type}