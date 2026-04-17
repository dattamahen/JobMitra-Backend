"""
Seed 10 diversified job listings into MongoDB.
Run: py seed_jobs.py
"""

import asyncio
import os
import uuid
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

HR_IDS = [
    "a1320785-0b1c-4bee-92e5-41eb70b59099",
    "84942b37-e4b2-4bba-8b08-a0f6be304d58",
]

def make_job_id(title, company):
    slug = f"{title}-{company}".lower().replace(" ", "-").replace(".", "")
    return f"{slug}-{uuid.uuid4().hex[:6]}"

JOBS = [
    {
        "title": "Senior React Developer",
        "company": "TechNova Solutions",
        "location": {"city": "Mumbai", "state": "Maharashtra", "country": "India", "is_remote": False, "timezone": "IST"},
        "employment_type": "full-time",
        "experience_level": "senior",
        "job_type": "hybrid",
        "salary": {"min": 2000000, "max": 3500000, "currency": "INR", "period": "yearly", "is_negotiable": True},
        "description": "We are seeking a Senior React Developer to lead frontend architecture and build high-performance web applications. You will mentor junior developers and drive best practices across the team.",
        "requirements": ["5+ years of React.js experience", "Strong TypeScript skills", "Experience with state management (Redux/Zustand)", "CI/CD pipeline knowledge"],
        "responsibilities": ["Architect and build scalable React applications", "Code reviews and mentoring", "Collaborate with backend and design teams", "Performance optimization"],
        "skills_required": ["React.js", "TypeScript", "Redux", "REST APIs", "Git"],
        "skills_preferred": ["Next.js", "GraphQL", "AWS"],
        "benefits": ["Health Insurance", "Stock Options", "Flexible Hours", "Learning Budget"],
        "company_info": {"company_size": "201-500", "industry": "Technology", "website": "https://technova.example.com", "logo_url": None, "description": "TechNova Solutions builds enterprise SaaS products for the fintech industry."},
        "hr_contact": {"name": "Priya Sharma", "email": "priya@technova.example.com", "phone": "+919876543210", "title": "Senior Recruiter", "department": "Human Resources"},
        "tags": ["react", "frontend", "senior", "hybrid"],
    },
    {
        "title": "Data Scientist",
        "company": "AnalytiQ Labs",
        "location": {"city": "Hyderabad", "state": "Telangana", "country": "India", "is_remote": True, "timezone": "IST"},
        "employment_type": "full-time",
        "experience_level": "mid",
        "job_type": "remote",
        "salary": {"min": 1500000, "max": 2500000, "currency": "INR", "period": "yearly", "is_negotiable": True},
        "description": "Join our data science team to build ML models that drive business decisions. Work with large datasets, develop predictive models, and present insights to stakeholders.",
        "requirements": ["3+ years in data science or ML", "Strong Python and SQL skills", "Experience with ML frameworks (scikit-learn, TensorFlow, or PyTorch)", "Statistics background"],
        "responsibilities": ["Build and deploy ML models", "Analyze large datasets for patterns", "Create dashboards and reports", "Collaborate with product teams"],
        "skills_required": ["Python", "Machine Learning", "SQL", "Pandas", "Statistics"],
        "skills_preferred": ["TensorFlow", "Spark", "Tableau", "AWS SageMaker"],
        "benefits": ["Remote Work", "Health Insurance", "Conference Budget", "Home Office Stipend"],
        "company_info": {"company_size": "51-200", "industry": "Data Analytics", "website": "https://analytiq.example.com", "logo_url": None, "description": "AnalytiQ Labs provides AI-driven analytics solutions for healthcare and retail."},
        "hr_contact": {"name": "Rahul Verma", "email": "rahul@analytiq.example.com", "phone": "+919123456789", "title": "Talent Acquisition Lead", "department": "Human Resources"},
        "tags": ["data-science", "machine-learning", "remote", "python"],
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudBridge Inc",
        "location": {"city": "Pune", "state": "Maharashtra", "country": "India", "is_remote": False, "timezone": "IST"},
        "employment_type": "full-time",
        "experience_level": "mid",
        "job_type": "onsite",
        "salary": {"min": 1200000, "max": 2000000, "currency": "INR", "period": "yearly", "is_negotiable": False},
        "description": "We need a DevOps Engineer to manage our cloud infrastructure, CI/CD pipelines, and ensure 99.9% uptime for our microservices platform.",
        "requirements": ["3+ years DevOps experience", "Strong AWS or Azure knowledge", "Docker and Kubernetes expertise", "Scripting (Bash/Python)"],
        "responsibilities": ["Manage AWS cloud infrastructure", "Build and maintain CI/CD pipelines", "Monitor system health and performance", "Implement security best practices"],
        "skills_required": ["AWS", "Docker", "Kubernetes", "Terraform", "Linux"],
        "skills_preferred": ["Ansible", "Prometheus", "Grafana", "Jenkins"],
        "benefits": ["Health Insurance", "Gym Membership", "Annual Bonus", "Certification Reimbursement"],
        "company_info": {"company_size": "51-200", "industry": "Cloud Services", "website": "https://cloudbridge.example.com", "logo_url": None, "description": "CloudBridge helps enterprises migrate and manage cloud-native applications."},
        "hr_contact": {"name": "Anita Desai", "email": "anita@cloudbridge.example.com", "phone": "+919988776655", "title": "HR Manager", "department": "Human Resources"},
        "tags": ["devops", "aws", "kubernetes", "cloud"],
    },
    {
        "title": "UI/UX Designer",
        "company": "PixelCraft Studio",
        "location": {"city": "Bengaluru", "state": "Karnataka", "country": "India", "is_remote": True, "timezone": "IST"},
        "employment_type": "full-time",
        "experience_level": "mid",
        "job_type": "remote",
        "salary": {"min": 1000000, "max": 1800000, "currency": "INR", "period": "yearly", "is_negotiable": True},
        "description": "Design intuitive and beautiful user experiences for our mobile and web products. You will own the design process from research to high-fidelity prototypes.",
        "requirements": ["3+ years UI/UX design experience", "Proficiency in Figma", "Strong portfolio showcasing mobile and web designs", "User research experience"],
        "responsibilities": ["Create wireframes and prototypes", "Conduct user research and usability testing", "Maintain design system", "Collaborate with developers for pixel-perfect implementation"],
        "skills_required": ["Figma", "UI Design", "UX Research", "Prototyping", "Design Systems"],
        "skills_preferred": ["Adobe XD", "Framer", "HTML/CSS", "Motion Design"],
        "benefits": ["Remote Work", "Health Insurance", "Creative Leave", "Design Tool Subscriptions"],
        "company_info": {"company_size": "11-50", "industry": "Design", "website": "https://pixelcraft.example.com", "logo_url": None, "description": "PixelCraft Studio is a design agency creating digital experiences for startups and enterprises."},
        "hr_contact": {"name": "Meera Nair", "email": "meera@pixelcraft.example.com", "phone": "+919876501234", "title": "People Operations", "department": "Human Resources"},
        "tags": ["design", "ui-ux", "figma", "remote"],
    },
    {
        "title": "Backend Engineer (Java)",
        "company": "FinServe Technologies",
        "location": {"city": "Chennai", "state": "Tamil Nadu", "country": "India", "is_remote": False, "timezone": "IST"},
        "employment_type": "full-time",
        "experience_level": "senior",
        "job_type": "onsite",
        "salary": {"min": 2500000, "max": 4000000, "currency": "INR", "period": "yearly", "is_negotiable": True},
        "description": "Build robust, high-throughput backend systems for our digital banking platform. You will work on transaction processing, API design, and system reliability.",
        "requirements": ["5+ years Java/Spring Boot experience", "Microservices architecture knowledge", "Experience with relational databases", "Understanding of financial systems"],
        "responsibilities": ["Design and develop microservices", "Optimize database queries and performance", "Ensure compliance with banking regulations", "Write comprehensive unit and integration tests"],
        "skills_required": ["Java", "Spring Boot", "PostgreSQL", "Microservices", "REST APIs"],
        "skills_preferred": ["Kafka", "Redis", "gRPC", "AWS"],
        "benefits": ["Health Insurance", "Performance Bonus", "Retirement Plan", "Meal Allowance"],
        "company_info": {"company_size": "501-1000", "industry": "Fintech", "website": "https://finserve.example.com", "logo_url": None, "description": "FinServe Technologies powers digital banking for 10M+ users across India."},
        "hr_contact": {"name": "Karthik Rajan", "email": "karthik@finserve.example.com", "phone": "+919012345678", "title": "Technical Recruiter", "department": "Human Resources"},
        "tags": ["java", "backend", "fintech", "senior"],
    },
    {
        "title": "Mobile App Developer (Flutter)",
        "company": "AppVerse",
        "location": {"city": "Delhi", "state": "Delhi", "country": "India", "is_remote": False, "timezone": "IST"},
        "employment_type": "full-time",
        "experience_level": "entry",
        "job_type": "hybrid",
        "salary": {"min": 600000, "max": 1000000, "currency": "INR", "period": "yearly", "is_negotiable": True},
        "description": "We are looking for a Flutter developer to build cross-platform mobile apps. Great opportunity for freshers with strong Dart fundamentals and a passion for mobile development.",
        "requirements": ["0-2 years Flutter/Dart experience", "Understanding of mobile app lifecycle", "Basic knowledge of REST APIs", "Published app or strong portfolio preferred"],
        "responsibilities": ["Develop cross-platform mobile apps", "Integrate REST APIs", "Write clean, testable code", "Participate in code reviews"],
        "skills_required": ["Flutter", "Dart", "REST APIs", "Git", "Mobile Development"],
        "skills_preferred": ["Firebase", "Bloc/Riverpod", "iOS/Android native basics"],
        "benefits": ["Health Insurance", "Mentorship Program", "Flexible Hours", "Snacks & Beverages"],
        "company_info": {"company_size": "11-50", "industry": "Mobile Apps", "website": "https://appverse.example.com", "logo_url": None, "description": "AppVerse builds consumer mobile apps in health, fitness, and lifestyle."},
        "hr_contact": {"name": "Sneha Gupta", "email": "sneha@appverse.example.com", "phone": "+919876512345", "title": "HR Executive", "department": "Human Resources"},
        "tags": ["flutter", "mobile", "entry-level", "hybrid"],
    },
    {
        "title": "Cybersecurity Analyst",
        "company": "SecureNet Global",
        "location": {"city": "Noida", "state": "Uttar Pradesh", "country": "India", "is_remote": False, "timezone": "IST"},
        "employment_type": "full-time",
        "experience_level": "mid",
        "job_type": "onsite",
        "salary": {"min": 1400000, "max": 2200000, "currency": "INR", "period": "yearly", "is_negotiable": False},
        "description": "Protect our enterprise clients from cyber threats. You will perform vulnerability assessments, incident response, and security audits across cloud and on-prem environments.",
        "requirements": ["3+ years in cybersecurity", "SIEM tools experience", "Knowledge of OWASP Top 10", "Security certifications preferred (CEH, CISSP)"],
        "responsibilities": ["Conduct vulnerability assessments and penetration testing", "Monitor and respond to security incidents", "Develop security policies and procedures", "Train teams on security best practices"],
        "skills_required": ["Network Security", "SIEM", "Penetration Testing", "Incident Response", "Firewalls"],
        "skills_preferred": ["AWS Security", "CISSP", "Splunk", "Python scripting"],
        "benefits": ["Health Insurance", "Certification Sponsorship", "Annual Bonus", "Work-Life Balance"],
        "company_info": {"company_size": "201-500", "industry": "Cybersecurity", "website": "https://securenet.example.com", "logo_url": None, "description": "SecureNet Global provides managed security services to Fortune 500 companies."},
        "hr_contact": {"name": "Vikram Singh", "email": "vikram@securenet.example.com", "phone": "+919871234567", "title": "Recruitment Manager", "department": "Human Resources"},
        "tags": ["cybersecurity", "security", "analyst", "onsite"],
    },
    {
        "title": "Full Stack Developer (MERN)",
        "company": "WebStack Labs",
        "location": {"city": "Jaipur", "state": "Rajasthan", "country": "India", "is_remote": True, "timezone": "IST"},
        "employment_type": "contract",
        "experience_level": "mid",
        "job_type": "remote",
        "salary": {"min": 80000, "max": 120000, "currency": "INR", "period": "monthly", "is_negotiable": True},
        "description": "6-month contract for a MERN stack developer to build a SaaS platform from scratch. Ideal for developers who love greenfield projects and fast-paced environments.",
        "requirements": ["3+ years MERN stack experience", "Experience building SaaS products", "Strong MongoDB and Node.js skills", "Familiarity with cloud deployment"],
        "responsibilities": ["Build full-stack features end to end", "Design database schemas", "Deploy and maintain on AWS", "Write API documentation"],
        "skills_required": ["MongoDB", "Express.js", "React.js", "Node.js", "JavaScript"],
        "skills_preferred": ["TypeScript", "Docker", "AWS", "Socket.io"],
        "benefits": ["Remote Work", "Flexible Schedule", "Performance Bonus", "Potential Full-Time Conversion"],
        "company_info": {"company_size": "1-10", "industry": "SaaS", "website": "https://webstacklabs.example.com", "logo_url": None, "description": "WebStack Labs is a bootstrapped startup building project management tools."},
        "hr_contact": {"name": "Arjun Mehta", "email": "arjun@webstacklabs.example.com", "phone": "+919845671234", "title": "Founder & CEO", "department": "Management"},
        "tags": ["mern", "fullstack", "contract", "remote", "saas"],
    },
    {
        "title": "AI/ML Engineer",
        "company": "NeuralPath AI",
        "location": {"city": "Bengaluru", "state": "Karnataka", "country": "India", "is_remote": False, "timezone": "IST"},
        "employment_type": "full-time",
        "experience_level": "senior",
        "job_type": "hybrid",
        "salary": {"min": 3000000, "max": 5000000, "currency": "INR", "period": "yearly", "is_negotiable": True},
        "description": "Join our AI research team to build production-grade LLM applications, RAG pipelines, and computer vision systems. Work at the cutting edge of generative AI.",
        "requirements": ["5+ years ML/AI experience", "Strong Python and deep learning skills", "Experience with LLMs and prompt engineering", "Published research or patents preferred"],
        "responsibilities": ["Design and train ML models for production", "Build RAG and LLM-based applications", "Optimize model inference and latency", "Collaborate with research and product teams"],
        "skills_required": ["Python", "PyTorch", "LLMs", "NLP", "Deep Learning"],
        "skills_preferred": ["LangChain", "Vector Databases", "MLOps", "Computer Vision", "Hugging Face"],
        "benefits": ["Health Insurance", "Stock Options", "Research Budget", "GPU Access", "Conference Travel"],
        "company_info": {"company_size": "51-200", "industry": "Artificial Intelligence", "website": "https://neuralpath.example.com", "logo_url": None, "description": "NeuralPath AI builds enterprise AI solutions using cutting-edge generative AI technology."},
        "hr_contact": {"name": "Deepa Krishnan", "email": "deepa@neuralpath.example.com", "phone": "+919765432100", "title": "Head of Talent", "department": "Human Resources"},
        "tags": ["ai", "ml", "llm", "deep-learning", "senior"],
    },
    {
        "title": "QA Automation Engineer",
        "company": "QualityFirst Software",
        "location": {"city": "Kolkata", "state": "West Bengal", "country": "India", "is_remote": False, "timezone": "IST"},
        "employment_type": "full-time",
        "experience_level": "entry",
        "job_type": "onsite",
        "salary": {"min": 500000, "max": 800000, "currency": "INR", "period": "yearly", "is_negotiable": True},
        "description": "Kickstart your QA career by building automated test suites for web and mobile applications. We provide structured training and mentorship for freshers.",
        "requirements": ["0-2 years QA experience", "Basic programming knowledge (Java/Python)", "Understanding of testing concepts", "Eagerness to learn automation tools"],
        "responsibilities": ["Write and maintain automated test scripts", "Execute regression and smoke tests", "Report and track bugs", "Collaborate with developers on quality improvements"],
        "skills_required": ["Selenium", "Java", "Manual Testing", "Test Automation", "Bug Tracking"],
        "skills_preferred": ["Cypress", "Appium", "JMeter", "Postman", "CI/CD"],
        "benefits": ["Health Insurance", "Training Program", "Mentorship", "Career Growth Path"],
        "company_info": {"company_size": "51-200", "industry": "Software Testing", "website": "https://qualityfirst.example.com", "logo_url": None, "description": "QualityFirst Software provides QA and testing services to global tech companies."},
        "hr_contact": {"name": "Suman Das", "email": "suman@qualityfirst.example.com", "phone": "+919834567890", "title": "HR Coordinator", "department": "Human Resources"},
        "tags": ["qa", "automation", "testing", "entry-level", "selenium"],
    },
]


async def seed():
    uri = os.getenv("MONGO_URI")
    client = AsyncIOMotorClient(uri)
    db_name = uri.split("/")[-1].split("?")[0]
    db = client[db_name]
    collection = db["jobs"]

    now = datetime.utcnow()
    docs = []
    for i, job in enumerate(JOBS):
        job_id = make_job_id(job["title"], job["company"])
        doc = {
            **job,
            "job_id": job_id,
            "application_deadline": None,
            "external_apply_url": None,
            "application_instructions": None,
            "learning_resources": [],
            "posted_date": now - timedelta(days=i * 3),
            "updated_date": now - timedelta(days=i * 3),
            "is_active": True,
            "posted_by_hr_id": HR_IDS[i % len(HR_IDS)],
            "views_count": 0,
            "applications_count": [],
            "source": "internal",
            "job_score": None,
            "match_percentage": None,
            "applications_received": [],
        }
        docs.append(doc)

    result = await collection.insert_many(docs)
    print(f"Inserted {len(result.inserted_ids)} jobs successfully!")
    for doc in docs:
        print(f"  - {doc['title']} @ {doc['company']} ({doc['job_type']}, {doc['experience_level']})")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
