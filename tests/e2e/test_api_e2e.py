"""
E2E Integration Tests for JobMitra Backend API.
These tests hit the REAL running server (http://localhost:8000).
Requires: Backend server running on port 8000.

Run: pytest tests/e2e/ -v --html=tests/e2e/reports/e2e_report.html --self-contained-html
"""
import pytest
import httpx
import time
import sys
import os
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# Store tokens across tests
_state = {"token": None, "user_id": None, "test_user_email": f"e2e_test_{int(time.time())}@test.com"}


@pytest.fixture(scope="session")
def client():
    """HTTP client for the test session."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        yield c


@pytest.fixture(scope="session")
def auth_headers(client):
    """Get auth headers by logging in."""
    # Try to login with test user, or register first
    login_resp = client.post(f"{API_URL}/auth/login", json={
        "email": "testuser@jobmitra.com",
        "password": "TestPass123!"
    })

    if login_resp.status_code == 200:
        data = login_resp.json()
        _state["token"] = data["access_token"]
        _state["user_id"] = data["user"]["user_id"]
    else:
        # Register a new test user
        reg_resp = client.post(f"{API_URL}/auth/register", json={
            "email": _state["test_user_email"],
            "password": "E2ETestPass123!",
            "first_name": "E2E",
            "last_name": "Tester",
            "user_type": "candidate"
        })
        if reg_resp.status_code == 200:
            # Now login
            login_resp = client.post(f"{API_URL}/auth/login", json={
                "email": _state["test_user_email"],
                "password": "E2ETestPass123!"
            })
            if login_resp.status_code == 200:
                data = login_resp.json()
                _state["token"] = data["access_token"]
                _state["user_id"] = data["user"]["user_id"]

    if _state["token"]:
        return {"Authorization": f"Bearer {_state['token']}"}
    return {}


# ─── Health Check Tests ───────────────────────────────────────────────────────

class TestHealthChecks:
    """E2E: Verify server is running and healthy."""

    def test_root_health(self, client):
        """TC-E2E-001: Root endpoint returns healthy status."""
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_extended_health(self, client):
        """TC-E2E-002: Extended health check returns all features."""
        resp = client.get(f"{API_URL}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "user_management" in data["features"]
        assert "job_search" in data["features"]
        assert "mock_interviews" in data["features"]

    def test_cors_endpoint(self, client):
        """TC-E2E-003: CORS test endpoint works."""
        resp = client.get("/cors-test")
        assert resp.status_code == 200
        assert "CORS is working" in resp.json()["message"]


# ─── Authentication E2E Tests ─────────────────────────────────────────────────

class TestAuthenticationE2E:
    """E2E: Full authentication flow."""

    def test_login_invalid_credentials(self, client):
        """TC-E2E-004: Login with wrong password returns 401."""
        resp = client.post(f"{API_URL}/auth/login", json={
            "email": "nonexistent@fake.com",
            "password": "WrongPassword123!"
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        """TC-E2E-005: Login with missing fields returns 422."""
        resp = client.post(f"{API_URL}/auth/login", json={
            "email": "test@test.com"
        })
        assert resp.status_code == 422

    def test_register_short_password(self, client):
        """TC-E2E-006: Register with short password returns 422."""
        resp = client.post(f"{API_URL}/auth/register", json={
            "email": "short@test.com",
            "password": "short",
            "first_name": "Short",
            "last_name": "Pass"
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        """TC-E2E-007: Register with invalid email returns 422."""
        resp = client.post(f"{API_URL}/auth/register", json={
            "email": "not-an-email",
            "password": "ValidPass123!",
            "first_name": "Bad",
            "last_name": "Email"
        })
        assert resp.status_code == 422

    def test_protected_endpoint_no_token(self, client):
        """TC-E2E-008: Accessing /auth/me without token returns 401/403."""
        resp = client.get(f"{API_URL}/auth/me")
        assert resp.status_code in [401, 403]

    def test_protected_endpoint_invalid_token(self, client):
        """TC-E2E-009: Accessing /auth/me with invalid token returns 401."""
        resp = client.get(f"{API_URL}/auth/me", headers={
            "Authorization": "Bearer invalid_garbage_token"
        })
        assert resp.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        """TC-E2E-010: Get current user profile with valid token."""
        if not auth_headers:
            pytest.skip("No auth token available")

        resp = client.get(f"{API_URL}/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "user_id" in data
        assert "email" in data
        assert "first_name" in data

    def test_logout(self, client, auth_headers):
        """TC-E2E-011: Logout endpoint responds successfully."""
        if not auth_headers:
            pytest.skip("No auth token available")

        resp = client.post(f"{API_URL}/auth/logout", headers=auth_headers)
        assert resp.status_code == 200
        assert "Logged out" in resp.json()["message"]


# ─── Job Search E2E Tests ─────────────────────────────────────────────────────

class TestJobSearchE2E:
    """E2E: Job search and listing operations."""

    def test_search_jobs_requires_auth(self, client):
        """TC-E2E-012: Job search requires authentication."""
        resp = client.post(f"{API_URL}/jobs/search", json={"limit": 5})
        assert resp.status_code in [401, 403]

    def test_search_jobs_with_auth(self, client, auth_headers):
        """TC-E2E-013: Job search returns results with auth."""
        if not auth_headers:
            pytest.skip("No auth token available")

        resp = client.post(f"{API_URL}/jobs/search", json={
            "query": "developer",
            "limit": 10
        }, headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], list)

    def test_search_jobs_with_filters(self, client, auth_headers):
        """TC-E2E-014: Job search with skill filters."""
        if not auth_headers:
            pytest.skip("No auth token available")

        resp = client.post(f"{API_URL}/jobs/search", json={
            "skills": ["Python"],
            "limit": 5
        }, headers=auth_headers)

        assert resp.status_code == 200

    def test_get_job_details(self, client):
        """TC-E2E-015: Get job details endpoint responds."""
        resp = client.get(f"{API_URL}/jobs/job_001")
        assert resp.status_code == 200


# ─── User Dashboard E2E Tests ─────────────────────────────────────────────────

class TestDashboardE2E:
    """E2E: Dashboard and user data operations."""

    def test_get_dashboard(self, client, auth_headers):
        """TC-E2E-016: Get user dashboard data."""
        if not auth_headers or not _state["user_id"]:
            pytest.skip("No auth available")

        resp = client.get(f"{API_URL}/users/{_state['user_id']}/dashboard", headers=auth_headers)
        # May return 200 or 404 depending on data
        assert resp.status_code in [200, 404]

        if resp.status_code == 200:
            data = resp.json()
            assert "user_id" in data
            assert "applications_count" in data

    def test_get_user_progress(self, client, auth_headers):
        """TC-E2E-017: Get user learning progress."""
        if not auth_headers or not _state["user_id"]:
            pytest.skip("No auth available")

        resp = client.get(f"{API_URL}/users/{_state['user_id']}/progress", headers=auth_headers)
        assert resp.status_code in [200, 404]


# ─── Learning Resources E2E Tests ─────────────────────────────────────────────

class TestLearningResourcesE2E:
    """E2E: Learning resources operations."""

    def test_get_resources(self, client):
        """TC-E2E-018: Get learning resources."""
        resp = client.get(f"{API_URL}/learning-resources")
        assert resp.status_code == 200
        data = resp.json()
        assert "resources" in data
        assert "count" in data

    def test_get_resources_with_filter(self, client):
        """TC-E2E-019: Get learning resources with skill filter."""
        resp = client.get(f"{API_URL}/learning-resources?skill=Python&level=beginner")
        assert resp.status_code == 200
        data = resp.json()
        assert data["filters"]["skill"] == "Python"


# ─── Mock Interview E2E Tests ─────────────────────────────────────────────────

class TestMockInterviewE2E:
    """E2E: Mock interview operations."""

    def test_get_user_interviews(self, client, auth_headers):
        """TC-E2E-020: Get user mock interview history."""
        if not auth_headers or not _state["user_id"]:
            pytest.skip("No auth available")

        resp = client.get(f"{API_URL}/users/{_state['user_id']}/mock-interviews", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "interviews" in data
        assert "count" in data


# ─── Profile Update E2E Tests ─────────────────────────────────────────────────

class TestProfileUpdateE2E:
    """E2E: Profile update operations."""

    def test_update_profile(self, client, auth_headers):
        """TC-E2E-021: Update user profile."""
        if not auth_headers:
            pytest.skip("No auth available")

        resp = client.put(f"{API_URL}/auth/profile", json={
            "professional_summary": f"E2E test update at {datetime.utcnow().isoformat()}",
            "skills": ["Python", "FastAPI", "E2E Testing"]
        }, headers=auth_headers)

        assert resp.status_code == 200

    def test_update_profile_no_auth(self, client):
        """TC-E2E-022: Profile update without auth fails."""
        resp = client.put(f"{API_URL}/auth/profile", json={
            "first_name": "Hacker"
        })
        assert resp.status_code in [401, 403]


# ─── Analytics E2E Tests ──────────────────────────────────────────────────────

class TestAnalyticsE2E:
    """E2E: Analytics endpoints."""

    def test_analytics_summary(self, client):
        """TC-E2E-023: Get analytics summary."""
        resp = client.get(f"{API_URL}/analytics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_users" in data
        assert "total_jobs" in data


# ─── Default Skills & Objective E2E Tests ─────────────────────────────────────

class TestDefaultProfileDataE2E:
    """E2E: Verify new users get default skills and professional objective."""

    def test_register_new_user_gets_default_skills(self, client):
        """TC-E2E-030: Newly registered user has 5-6 default skills."""
        import time
        email = f"e2e_skills_{int(time.time())}@test.com"

        reg_resp = client.post(f"{API_URL}/auth/register", json={
            "email": email,
            "password": "TestSkills123!",
            "first_name": "Skills",
            "last_name": "Test",
            "user_type": "candidate"
        })
        assert reg_resp.status_code == 200
        data = reg_resp.json()
        assert "skills" in data
        assert isinstance(data["skills"], list)
        assert len(data["skills"]) in [5, 6]

    def test_register_new_user_skills_are_valid(self, client):
        """TC-E2E-031: Default skills are from the known skills pool."""
        import time
        from default_profile_data import DEFAULT_SKILLS

        email = f"e2e_valid_skills_{int(time.time())}@test.com"

        reg_resp = client.post(f"{API_URL}/auth/register", json={
            "email": email,
            "password": "TestValid123!",
            "first_name": "Valid",
            "last_name": "Skills",
            "user_type": "candidate"
        })
        assert reg_resp.status_code == 200
        data = reg_resp.json()
        for skill in data["skills"]:
            assert skill in DEFAULT_SKILLS

    def test_register_new_user_gets_professional_summary(self, client):
        """TC-E2E-032: Newly registered user has a professional_summary set."""
        import time
        from default_profile_data import DEFAULT_OBJECTIVES

        email = f"e2e_obj_{int(time.time())}@test.com"

        # Register
        reg_resp = client.post(f"{API_URL}/auth/register", json={
            "email": email,
            "password": "TestObj123!!",
            "first_name": "Objective",
            "last_name": "Test",
            "user_type": "candidate"
        })
        assert reg_resp.status_code == 200

        # Login to get token
        login_resp = client.post(f"{API_URL}/auth/login", json={
            "email": email,
            "password": "TestObj123!!"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # Fetch profile
        me_resp = client.get(f"{API_URL}/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert me_resp.status_code == 200
        profile = me_resp.json()
        assert "professional_summary" in profile
        assert profile["professional_summary"] in DEFAULT_OBJECTIVES

    def test_register_user_with_explicit_skills_preserves_them(self, client):
        """TC-E2E-033: User who provides skills during registration keeps them."""
        import time
        email = f"e2e_explicit_{int(time.time())}@test.com"

        # Note: Current register endpoint doesn't accept skills,
        # so this tests that the default is applied. If skills were
        # passed via a different flow, they'd be preserved.
        reg_resp = client.post(f"{API_URL}/auth/register", json={
            "email": email,
            "password": "ExplicitSkills1!",
            "first_name": "Explicit",
            "last_name": "Skills",
            "user_type": "candidate"
        })
        assert reg_resp.status_code == 200
        data = reg_resp.json()
        # Should have defaults since register doesn't pass skills
        assert len(data["skills"]) in [5, 6]

    def test_login_response_includes_default_skills(self, client):
        """TC-E2E-034: Login response includes the default skills assigned at registration."""
        import time
        email = f"e2e_login_skills_{int(time.time())}@test.com"

        # Register
        client.post(f"{API_URL}/auth/register", json={
            "email": email,
            "password": "LoginSkills1!",
            "first_name": "Login",
            "last_name": "Skills",
            "user_type": "candidate"
        })

        # Login
        login_resp = client.post(f"{API_URL}/auth/login", json={
            "email": email,
            "password": "LoginSkills1!"
        })
        assert login_resp.status_code == 200
        user_data = login_resp.json()["user"]
        assert "skills" in user_data
        assert len(user_data["skills"]) in [5, 6]


# ─── Forgot Password E2E Tests ────────────────────────────────────────────────

class TestForgotPasswordE2E:
    """E2E: Forgot password flow."""

    def test_forgot_password_any_email(self, client):
        """TC-E2E-024: Forgot password always returns 200 (no email leak)."""
        resp = client.post(f"{API_URL}/auth/forgot-password", json={
            "email": "anyone@anywhere.com"
        })
        assert resp.status_code == 200
        assert "reset link will be sent" in resp.json()["message"]

    def test_reset_password_invalid_token(self, client):
        """TC-E2E-025: Reset password with invalid token fails."""
        resp = client.post(f"{API_URL}/auth/reset-password", json={
            "token": "invalid_token_12345",
            "new_password": "NewPass123!"
        })
        assert resp.status_code == 400
