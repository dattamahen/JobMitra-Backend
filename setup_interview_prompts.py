from pymongo import MongoClient
from datetime import datetime

def create_comprehensive_prompts():
    """Create all interview prompts including the new detailed ones"""
    prompts = [
        # Universal Question Generator
        {
            "role": "any",
            "experience_level": "any",
            "experience_years_min": 0,
            "experience_years_max": 99,
            "prompt_type": "question_generator",
            "prompt_template": """You are an expert technical interviewer.

Your task:
- Analyze the provided user details JSON.
- Generate high-quality interview questions tailored to the role, experience, and skills.
- Adjust difficulty based on years of experience.
- Ask clear, concise, real-world interview questions.
- Do NOT add explanations or answers.
- Return output in STRICT JSON only.
- Do NOT include markdown, comments, or extra text.

Question guidelines:
- 40% technical questions
- 30% problem-solving / scenario-based questions
- 20% fundamentals & theory
- 10% behavioral (role-relevant)

Difficulty rules:
- 0–2 years: beginner to intermediate
- 3–5 years: intermediate to advanced
- 6+ years: advanced, system design, leadership

If generate_questions is false, return an empty questions array.""",
            "question_count": 10,
            "difficulty": "adaptive",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Senior Associate (3-5 years) - Expertise and Leadership
        {
            "role": "any",
            "experience_level": "senior_associate",
            "experience_years_min": 3,
            "experience_years_max": 5,
            "prompt_type": "expertise_leadership",
            "prompt_template": "You are a recruiter for a Senior Associate Position Title role in any industry. Candidate Profile: [As above]. Interview Focus: Assess technical depth, project leadership, and efficiency improvements. Greet the candidate, then ask 8–10 questions covering: 1. Advanced skills applied in key projects 2. Leadership or initiative in project execution 3. Process improvements or optimizations made 4. Collaboration with diverse teams 5. Handling complex project challenges 6. Tools or methodologies for efficiency 7. Mentoring or guiding junior colleagues 8. Alignment with role responsibilities. Provide feedback after each answer, focusing on expertise. End with a summary of strengths and leadership potential.",
            "question_count": 9,
            "difficulty": "medium",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Senior Associate - Impact and Innovation
        {
            "role": "any",
            "experience_level": "senior_associate",
            "experience_years_min": 3,
            "experience_years_max": 5,
            "prompt_type": "impact_innovation",
            "prompt_template": "You are an interviewer for a Senior Associate Position Title position. Candidate Profile: [As above]. Interview Focus: Evaluate project impact, innovation, and strategic thinking. Start with an introduction, then ask 9 questions covering: 1. A project with significant measurable impact 2. Innovative approaches or solutions implemented 3. Collaboration to achieve project goals 4. Tools or systems used for efficiency 5. Managing project risks or setbacks 6. Technical depth relevant to the role 7. Supporting team growth or development 8. Career goals in the industry 9. Handling high-pressure scenarios. Offer feedback on each response, emphasizing innovation. Conclude with career progression advice.",
            "question_count": 9,
            "difficulty": "medium",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Consultant (5-7 years) - Advisory and Solutions
        {
            "role": "consultant",
            "experience_level": "consultant",
            "experience_years_min": 5,
            "experience_years_max": 7,
            "prompt_type": "advisory_solutions",
            "prompt_template": "You are a hiring manager for a Consultant Position Title role at a professional services company. Candidate Profile: [As above]. Interview Focus: Assess advisory capabilities, stakeholder engagement, and strategic impact. Greet the candidate, then ask 10 questions covering: 1. Delivering solutions to stakeholders or clients 2. Strategic approaches in complex projects 3. Collaboration with cross-functional teams 4. Tools or frameworks used in projects 5. Managing stakeholder expectations 6. Problem-solving in high-stakes scenarios 7. Technical or analytical skills for the role 8. Driving measurable project outcomes 9. Adaptability to changing requirements 10. Career aspirations as a consultant. Provide feedback after each answer, focusing on advisory skills. End with a summary of strengths and growth areas.",
            "question_count": 10,
            "difficulty": "hard",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Consultant - Strategic Thinking
        {
            "role": "consultant",
            "experience_level": "consultant",
            "experience_years_min": 5,
            "experience_years_max": 7,
            "prompt_type": "strategic_thinking",
            "prompt_template": "You are an interviewer for a Consultant Position Title position in any sector. Candidate Profile: [As above]. Interview Focus: Evaluate strategic problem-solving, client focus, and collaboration. Start professionally, then ask 9–10 questions covering: 1. A project requiring strategic decision-making 2. Engaging stakeholders to align on goals 3. Tools or methods for project success 4. Resolving conflicts or challenges 5. Measuring project impact or success 6. Role-specific technical expertise 7. Leading or supporting team efforts 8. Adapting to client or project changes 9. Long-term career vision. Offer feedback on each response, highlighting strategy. Conclude with advice on consulting excellence.",
            "question_count": 10,
            "difficulty": "hard",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Senior Consultant (7-10 years) - Expert Leadership
        {
            "role": "senior_consultant",
            "experience_level": "senior_consultant",
            "experience_years_min": 7,
            "experience_years_max": 10,
            "prompt_type": "expert_leadership",
            "prompt_template": "You are a senior recruiter for a Senior Consultant Position Title role in any industry. Candidate Profile: [As above]. Interview Focus: Assess deep expertise, leadership, and mentoring capabilities. Greet the candidate, then ask 10–12 questions covering: 1. Leading complex projects with high impact 2. Advanced skills applied in advisory roles 3. Mentoring or guiding team members 4. Tools or strategies for project success 5. Managing stakeholder relationships 6. Solving intricate project challenges 7. Driving innovation in projects 8. Role-specific technical depth 9. Aligning projects with strategic goals 10. Career leadership aspirations. Provide feedback after each answer, focusing on expertise. End with a summary of leadership potential.",
            "question_count": 11,
            "difficulty": "hard",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Senior Consultant - Innovation and Risk Management
        {
            "role": "senior_consultant",
            "experience_level": "senior_consultant",
            "experience_years_min": 7,
            "experience_years_max": 10,
            "prompt_type": "innovation_risk",
            "prompt_template": "You are an interviewer for a Senior Consultant Position Title position. Candidate Profile: [As above]. Interview Focus: Evaluate innovation, risk management, and strategic oversight. Start with an introduction, then ask 10 questions covering: 1. An innovative solution delivered in a project 2. Managing risks in high-stakes projects 3. Mentoring colleagues or junior staff 4. Tools or frameworks for efficiency 5. Aligning with stakeholder priorities 6. Resolving complex technical issues 7. Measuring long-term project impact 8. Role-specific expertise application 9. Adapting to dynamic challenges 10. Vision for career growth. Offer feedback on each response, emphasizing innovation. Conclude with career development insights.",
            "question_count": 10,
            "difficulty": "hard",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Manager (10+ years) - Leadership and Strategy
        {
            "role": "manager",
            "experience_level": "manager",
            "experience_years_min": 10,
            "experience_years_max": 99,
            "prompt_type": "leadership_strategy",
            "prompt_template": "You are a director conducting a mock interview for a Manager Position Title role in any sector. Candidate Profile: [As above]. Interview Focus: Assess leadership, strategic oversight, and team management. Greet the candidate, then ask 10–12 questions covering: 1. Leading teams to achieve project goals 2. Strategic decisions in complex projects 3. Managing team performance and growth 4. Tools or systems for operational efficiency 5. Aligning projects with organizational goals 6. Resolving team or project conflicts 7. Driving measurable business impact 8. Role-specific leadership expertise 9. Innovating in processes or workflows 10. Long-term career and leadership vision. Provide feedback after each answer, focusing on leadership. End with a summary of managerial strengths.",
            "question_count": 11,
            "difficulty": "expert",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Manager - Change and Impact
        {
            "role": "manager",
            "experience_level": "manager",
            "experience_years_min": 10,
            "experience_years_max": 99,
            "prompt_type": "change_impact",
            "prompt_template": "You are an executive for a Manager Position Title position in any industry. Candidate Profile: [As above]. Interview Focus: Evaluate change management, team leadership, and strategic impact. Start professionally, then ask 10–11 questions covering: 1. Driving change in teams or projects 2. Leading high-impact initiatives 3. Mentoring and developing team talent 4. Tools or strategies for scaling projects 5. Managing stakeholder or client expectations 6. Resolving critical project challenges 7. Measuring success in leadership roles 8. Role-specific strategic expertise 9. Innovating for organizational growth 10. Adapting to industry changes. Offer feedback on each response, highlighting impact. Conclude with advice on leadership excellence.",
            "question_count": 11,
            "difficulty": "expert",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    return prompts

def setup_interview_prompts_collection():
    """Initialize interview_prompts collection with comprehensive data"""
    client = MongoClient("mongodb://localhost:27017/")
    db = client["jobmitra"]
    
    if "interview_prompts" not in db.list_collection_names():
        db.create_collection("interview_prompts")
        print("Created interview_prompts collection")
    
    prompts = create_comprehensive_prompts()
    db.interview_prompts.delete_many({})
    result = db.interview_prompts.insert_many(prompts)
    
    print(f"Inserted {len(result.inserted_ids)} interview prompts")
    
    db.interview_prompts.create_index([
        ("role", 1),
        ("experience_level", 1),
        ("experience_years_min", 1),
        ("prompt_type", 1)
    ])
    
    print("Created indexes for interview_prompts collection")
    client.close()

if __name__ == "__main__":
    setup_interview_prompts_collection()