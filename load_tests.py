"""
Load Testing with Locust
Simulates real user behavior at scale.

Usage:
  Install:  pip install locust
  Run:      locust -f load_tests.py --host=http://localhost:8000
  UI:       Open http://localhost:8089
  Headless: locust -f load_tests.py --host=http://localhost:8000 --users=1000 --spawn-rate=50 --run-time=5m --headless

Scenarios:
  - 50% job seekers browsing/searching jobs
  - 25% authenticated users viewing dashboard/profile
  - 15% users performing AI operations (summary, interview)
  - 10% HR users posting jobs and checking applications
"""

import json
import random
from locust import HttpUser, task, between, tag


# Test credentials (seed these in your test DB)
TEST_USERS = [
    {"email": "testuser1@example.com", "password": "Test@123456"},
    {"email": "testuser2@example.com", "password": "Test@123456"},
    {"email": "testuser3@example.com", "password": "Test@123456"},
]

TEST_SKILLS = ["Python", "React", "Node.js", "Java", "Angular", "FastAPI", "MongoDB", "AWS", "Docker", "TypeScript"]


class JobSeekerUser(HttpUser):
    """Simulates a job seeker browsing and searching jobs."""
    weight = 50  # 50% of traffic
    wait_time = between(2, 5)

    def on_start(self):
        """Login on start."""
        creds = random.choice(TEST_USERS)
        response = self.client.post("/api/v1/auth/login", json=creds)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = ""
            self.headers = {}

    @task(5)
    @tag("search")
    def search_jobs(self):
        """Search jobs with random skills."""
        skills = random.sample(TEST_SKILLS, random.randint(1, 3))
        payload = {
            "page": random.randint(1, 5),
            "per_page": 10,
            "keywords": random.choice(["python", "react", "backend", "frontend", ""]),
            "user_skills": skills
        }
        self.client.post("/api/v1/jobs", json=payload, headers=self.headers, name="/api/v1/jobs [search]")

    @task(3)
    @tag("dashboard")
    def view_dashboard(self):
        """View dashboard."""
        self.client.get("/api/v1/dashboard", headers=self.headers)

    @task(2)
    @tag("profile")
    def view_profile(self):
        """View own profile."""
        self.client.get("/api/v1/auth/me", headers=self.headers)

    @task(1)
    @tag("applications")
    def view_applications(self):
        """View applied jobs."""
        self.client.get("/api/v1/profile/current", headers=self.headers)

    @task(1)
    def health_check(self):
        """Health check — baseline latency."""
        self.client.get("/")


class AIUser(HttpUser):
    """Simulates users performing AI-heavy operations."""
    weight = 15  # 15% of traffic
    wait_time = between(5, 15)  # AI ops are less frequent

    def on_start(self):
        creds = random.choice(TEST_USERS)
        response = self.client.post("/api/v1/auth/login", json=creds)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = ""
            self.headers = {}

    @task(3)
    @tag("ai")
    def generate_interview_questions(self):
        """Generate mock interview questions."""
        payload = {
            "role": random.choice(["Software Engineer", "Data Analyst", "Product Manager"]),
            "experience_years": random.randint(1, 10),
            "skills": random.sample(TEST_SKILLS, 3),
            "interview_type": random.choice(["technical", "behavioral"]),
            "generate_questions": True
        }
        self.client.post("/api/v1/get-interview-prompt", json=payload, headers=self.headers,
                         name="/api/v1/get-interview-prompt", timeout=35)

    @task(2)
    @tag("ai")
    def generate_professional_summary(self):
        """Generate AI professional summary."""
        payload = {
            "type": "professional_summary",
            "current_role": "Senior Developer",
            "experience_years": random.randint(2, 8),
            "skills": random.sample(TEST_SKILLS, 4),
            "work_experience": [{"company": "TechCorp", "position": "Developer"}]
        }
        self.client.post("/api/v1/profile/generate-ai-content", json=payload, headers=self.headers,
                         name="/api/v1/profile/generate-ai-content [summary]", timeout=35)

    @task(1)
    @tag("ai")
    def generate_job_description(self):
        """Generate AI job description."""
        payload = {
            "type": "job_description",
            "position": "Backend Engineer",
            "company": "StartupXYZ",
            "skills": random.sample(TEST_SKILLS, 3),
            "experience_years": 4,
            "is_current": False
        }
        self.client.post("/api/v1/profile/generate-ai-content", json=payload, headers=self.headers,
                         name="/api/v1/profile/generate-ai-content [job_desc]", timeout=35)


class DashboardUser(HttpUser):
    """Simulates users checking dashboard and profile repeatedly."""
    weight = 25  # 25% of traffic
    wait_time = between(3, 8)

    def on_start(self):
        creds = random.choice(TEST_USERS)
        response = self.client.post("/api/v1/auth/login", json=creds)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = ""
            self.headers = {}

    @task(4)
    @tag("dashboard")
    def view_dashboard(self):
        self.client.get("/api/v1/dashboard", headers=self.headers)

    @task(3)
    @tag("profile")
    def view_profile(self):
        self.client.get("/api/v1/auth/me", headers=self.headers)

    @task(2)
    @tag("profile")
    def update_profile(self):
        """Simulate profile update."""
        payload = {
            "professional_summary": f"Updated summary at {random.randint(1, 10000)}"
        }
        self.client.put("/api/v1/auth/profile", json=payload, headers=self.headers,
                        name="/api/v1/auth/profile [update]")

    @task(1)
    @tag("skills")
    def view_skills(self):
        self.client.get("/api/v1/skills/technical", headers=self.headers)

    @task(1)
    @tag("interviews")
    def view_interview_history(self):
        self.client.get("/api/v1/mock-interviews/history", headers=self.headers)


class HRUser(HttpUser):
    """Simulates HR users managing job postings."""
    weight = 10  # 10% of traffic
    wait_time = between(5, 12)

    def on_start(self):
        creds = random.choice(TEST_USERS)
        response = self.client.post("/api/v1/auth/login", json=creds)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = ""
            self.headers = {}

    @task(3)
    @tag("hr")
    def view_hr_dashboard(self):
        self.client.get("/api/v1/dashboard", headers=self.headers)

    @task(2)
    @tag("hr")
    def view_posted_jobs(self):
        self.client.get("/api/v1/hr/jobs?page=1&per_page=10", headers=self.headers,
                        name="/api/v1/hr/jobs")

    @task(1)
    @tag("hr")
    def view_applications_received(self):
        self.client.get("/api/v1/hr/applications-received", headers=self.headers,
                        name="/api/v1/hr/applications-received")
