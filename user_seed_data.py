"""
Seed data for creating multiple Indian users across various industries
"""

from datetime import datetime, timedelta
import hashlib
import secrets

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{pwd_hash.hex()}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, pwd_hash = stored_password.split(':')
        return pwd_hash == hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    except:
        return False

# Indian user seed data across various industries
INDIAN_USERS = [
    {
        "user_id": "user_001",
        "email": "arjun.sharma@email.com",
        "password": "JobSeeker@123",  # Will be hashed
        "username": "arjun_sharma",
        "user_type": "candidate",
        "personal_info": {
            "first_name": "Arjun",
            "last_name": "Sharma",
            "phone": "+91 98765 43210",
            "date_of_birth": "1990-05-15",
            "gender": "male",
            "location": {
                "city": "Bangalore",
                "state": "Karnataka",
                "country": "India",
                "pincode": "560001"
            }
        },
        "professional_info": {
            "current_role": "Senior Software Engineer",
            "current_company": "Infosys Limited",
            "total_experience": "8 years",
            "industry": "Information Technology",
            "skills": ["Java", "Spring Boot", "Microservices", "AWS", "React"],
            "current_salary": 2200000,  # 22 LPA
            "expected_salary": 2800000   # 28 LPA
        },
        "preferences": {
            "job_locations": ["Bangalore", "Mumbai", "Pune"],
            "remote_preference": "hybrid",
            "notice_period": "60 days"
        }
    },
    {
        "user_id": "user_002", 
        "email": "priya.patel@email.com",
        "password": "DataScience@456",
        "username": "priya_patel",
        "user_type": "candidate",
        "personal_info": {
            "first_name": "Priya",
            "last_name": "Patel",
            "phone": "+91 87654 32109",
            "date_of_birth": "1992-08-22",
            "gender": "female",
            "location": {
                "city": "Mumbai",
                "state": "Maharashtra", 
                "country": "India",
                "pincode": "400001"
            }
        },
        "professional_info": {
            "current_role": "Data Scientist",
            "current_company": "Tata Consultancy Services",
            "total_experience": "5 years",
            "industry": "Financial Services",
            "skills": ["Python", "Machine Learning", "SQL", "Tableau", "TensorFlow"],
            "current_salary": 1800000,  # 18 LPA
            "expected_salary": 2500000   # 25 LPA
        },
        "preferences": {
            "job_locations": ["Mumbai", "Pune", "Hyderabad"],
            "remote_preference": "remote",
            "notice_period": "30 days"
        }
    },
    {
        "user_id": "user_003",
        "email": "rajesh.kumar@email.com", 
        "password": "ProductMgr@789",
        "username": "rajesh_kumar",
        "user_type": "candidate",
        "personal_info": {
            "first_name": "Rajesh",
            "last_name": "Kumar",
            "phone": "+91 76543 21098",
            "date_of_birth": "1988-12-10",
            "gender": "male",
            "location": {
                "city": "Delhi",
                "state": "Delhi",
                "country": "India", 
                "pincode": "110001"
            }
        },
        "professional_info": {
            "current_role": "Product Manager",
            "current_company": "Flipkart",
            "total_experience": "10 years",
            "industry": "E-commerce",
            "skills": ["Product Strategy", "Agile", "Data Analysis", "User Research", "Leadership"],
            "current_salary": 3200000,  # 32 LPA
            "expected_salary": 4000000   # 40 LPA
        },
        "preferences": {
            "job_locations": ["Delhi", "Bangalore", "Mumbai"],
            "remote_preference": "hybrid",
            "notice_period": "90 days"
        }
    },
    {
        "user_id": "user_004",
        "email": "sneha.reddy@email.com",
        "password": "Designer@321",
        "username": "sneha_reddy",
        "user_type": "candidate",
        "personal_info": {
            "first_name": "Sneha",
            "last_name": "Reddy",
            "phone": "+91 65432 10987",
            "date_of_birth": "1994-03-18",
            "gender": "female",
            "location": {
                "city": "Hyderabad",
                "state": "Telangana",
                "country": "India",
                "pincode": "500001"
            }
        },
        "professional_info": {
            "current_role": "UX Designer",
            "current_company": "Swiggy",
            "total_experience": "4 years",
            "industry": "Food & Beverage",
            "skills": ["Figma", "User Research", "Prototyping", "Design Systems", "Adobe Creative Suite"],
            "current_salary": 1400000,  # 14 LPA
            "expected_salary": 1800000   # 18 LPA
        },
        "preferences": {
            "job_locations": ["Hyderabad", "Bangalore", "Pune"],
            "remote_preference": "remote",
            "notice_period": "45 days"
        }
    },
    {
        "user_id": "user_005",
        "email": "vikram.singh@email.com",
        "password": "DevOps@654",
        "username": "vikram_singh",
        "user_type": "candidate",
        "personal_info": {
            "first_name": "Vikram",
            "last_name": "Singh",
            "phone": "+91 54321 09876",
            "date_of_birth": "1989-07-25",
            "gender": "male",
            "location": {
                "city": "Pune",
                "state": "Maharashtra",
                "country": "India",
                "pincode": "411001"
            }
        },
        "professional_info": {
            "current_role": "DevOps Engineer",
            "current_company": "Tech Mahindra",
            "total_experience": "7 years",
            "industry": "Information Technology",
            "skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Terraform"],
            "current_salary": 2000000,  # 20 LPA
            "expected_salary": 2600000   # 26 LPA
        },
        "preferences": {
            "job_locations": ["Pune", "Mumbai", "Bangalore"],
            "remote_preference": "hybrid", 
            "notice_period": "60 days"
        }
    },
    {
        "user_id": "user_006",
        "email": "anita.joshi@email.com",
        "password": "Finance@987",
        "username": "anita_joshi",
        "user_type": "candidate",
        "personal_info": {
            "first_name": "Anita",
            "last_name": "Joshi",
            "phone": "+91 43210 98765",
            "date_of_birth": "1991-11-12", 
            "gender": "female",
            "location": {
                "city": "Chennai",
                "state": "Tamil Nadu",
                "country": "India",
                "pincode": "600001"
            }
        },
        "professional_info": {
            "current_role": "Financial Analyst",
            "current_company": "HDFC Bank",
            "total_experience": "6 years",
            "industry": "Banking & Financial Services",
            "skills": ["Financial Modeling", "Excel", "SQL", "Risk Analysis", "Regulatory Compliance"],
            "current_salary": 1600000,  # 16 LPA
            "expected_salary": 2200000   # 22 LPA
        },
        "preferences": {
            "job_locations": ["Chennai", "Bangalore", "Mumbai"],
            "remote_preference": "onsite",
            "notice_period": "45 days"
        }
    },
    {
        "user_id": "user_007",
        "email": "rohit.gupta@email.com",
        "password": "Marketing@147",
        "username": "rohit_gupta",
        "user_type": "candidate",
        "personal_info": {
            "first_name": "Rohit",
            "last_name": "Gupta",
            "phone": "+91 32109 87654",
            "date_of_birth": "1993-04-08",
            "gender": "male",
            "location": {
                "city": "Gurgaon",
                "state": "Haryana",
                "country": "India",
                "pincode": "122001"
            }
        },
        "professional_info": {
            "current_role": "Digital Marketing Manager",
            "current_company": "Paytm",
            "total_experience": "5 years",
            "industry": "Fintech",
            "skills": ["Digital Marketing", "SEO/SEM", "Google Analytics", "Social Media", "Content Strategy"],
            "current_salary": 1500000,  # 15 LPA
            "expected_salary": 2000000   # 20 LPA
        },
        "preferences": {
            "job_locations": ["Gurgaon", "Delhi", "Noida"],
            "remote_preference": "hybrid",
            "notice_period": "30 days"
        }
    },
    {
        "user_id": "user_008",
        "email": "kavya.nair@email.com",
        "password": "HRUser@12345",
        "username": "kavya_nair",
        "user_type": "hire",
        "company_name": "Wipro Limited",
        "personal_info": {
            "first_name": "Kavya",
            "last_name": "Nair",
            "phone": "+91 21098 76543",
            "date_of_birth": "1990-09-30",
            "gender": "female",
            "location": {
                "city": "Kochi",
                "state": "Kerala",
                "country": "India",
                "pincode": "682001"
            }
        },
        "professional_info": {
            "current_role": "HR Business Partner",
            "current_company": "Wipro Limited",
            "total_experience": "8 years",
            "industry": "Information Technology",
            "skills": ["Talent Acquisition", "Employee Relations", "Performance Management", "HRIS", "Compensation"],
            "current_salary": 1700000,  # 17 LPA
            "expected_salary": 2300000   # 23 LPA
        },
        "preferences": {
            "job_locations": ["Kochi", "Bangalore", "Chennai"],
            "remote_preference": "hybrid",
            "notice_period": "60 days"
        }
    }
]

def get_hashed_users():
    """Return users with hashed passwords"""
    users = []
    for user in INDIAN_USERS:
        user_copy = user.copy()
        user_copy["password_hash"] = hash_password(user["password"])
        del user_copy["password"]  # Remove plain text password
        user_copy["user_type"] = user.get("user_type", "candidate")  # Ensure user_type is included
        user_copy["created_at"] = datetime.now().isoformat()
        user_copy["updated_at"] = datetime.now().isoformat()
        user_copy["is_active"] = True
        user_copy["is_verified"] = True
        user_copy["last_login"] = None
        users.append(user_copy)
    return users
