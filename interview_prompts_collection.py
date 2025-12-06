from pymongo import MongoClient
from datetime import datetime

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
        "prompt_template": "You are conducting a {experience_level} level {role} interview...",
        "question_count": 5,
        "difficulty": "medium",
        "created_at": datetime,
        "updated_at": datetime
    }
    """
    
    # Sample prompts for different combinations
    sample_prompts = [
        {
            "role": "software_engineer",
            "experience_level": "junior",
            "technology": "python",
            "prompt_template": "You are conducting a junior-level Python software engineer interview. Ask 5 fundamental questions covering basic Python syntax, data structures, and simple problem-solving. Focus on: variables, loops, functions, lists/dictionaries, and basic OOP concepts.",
            "question_count": 5,
            "difficulty": "easy",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "software_engineer", 
            "experience_level": "mid",
            "technology": "python",
            "prompt_template": "You are conducting a mid-level Python software engineer interview. Ask 7 intermediate questions covering advanced Python concepts, design patterns, and system design basics. Focus on: decorators, generators, async/await, database integration, API design, testing, and performance optimization.",
            "question_count": 7,
            "difficulty": "medium",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "software_engineer",
            "experience_level": "senior", 
            "technology": "python",
            "prompt_template": "You are conducting a senior-level Python software engineer interview. Ask 10 advanced questions covering system architecture, scalability, leadership, and complex problem-solving. Focus on: microservices, distributed systems, performance tuning, code review practices, mentoring, and technical decision-making.",
            "question_count": 10,
            "difficulty": "hard",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "data_scientist",
            "experience_level": "junior",
            "technology": "python",
            "prompt_template": "You are conducting a junior-level Data Scientist interview. Ask 5 fundamental questions covering basic statistics, pandas, numpy, and simple ML concepts. Focus on: data cleaning, basic visualization, descriptive statistics, linear regression, and data manipulation.",
            "question_count": 5,
            "difficulty": "easy",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "role": "frontend_developer",
            "experience_level": "mid",
            "technology": "javascript",
            "prompt_template": "You are conducting a mid-level Frontend Developer interview. Ask 7 questions covering React/Angular, state management, performance optimization, and modern JavaScript. Focus on: component lifecycle, hooks, state management, bundling, responsive design, accessibility, and browser APIs.",
            "question_count": 7,
            "difficulty": "medium",
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