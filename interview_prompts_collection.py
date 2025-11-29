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
    role = user_profile.get('role', '').lower().replace(' ', '_')
    
    # Map experience to levels
    if 3 <= experience <= 5:
        return {'experience_level': 'senior_associate', 'role': 'any'}
    elif 5 <= experience <= 7:
        return {'experience_level': 'consultant', 'role': 'consultant'}
    elif 7 <= experience <= 10:
        return {'experience_level': 'senior_consultant', 'role': 'senior_consultant'}
    elif experience >= 10:
        return {'experience_level': 'manager', 'role': 'manager'}
    else:
        return {'experience_level': 'senior_associate', 'role': 'any'}  # default