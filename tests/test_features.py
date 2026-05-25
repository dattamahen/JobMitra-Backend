"""
Tests for Mock Interviews, Dashboard, and Learning Resources endpoints.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from datetime import datetime


@pytest.fixture
def app():
    with patch("db_simple.db") as mock_db:
        mock_db.fallback_mode = False
        mock_db.database = MagicMock()
        mock_db.connect_to_mongo = AsyncMock()
        mock_db.close_mongo_connection = AsyncMock()
        from app import create_app
        return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─── Mock Interview Tests ─────────────────────────────────────────────────────

class TestMockInterviews:
    """Test mock interview endpoints."""

    @pytest.mark.asyncio
    @patch("db_simple.create_mock_interview")
    async def test_create_mock_interview_success(self, mock_create, client):
        mock_create.return_value = "session_id_123"
        
        response = await client.post("/api/v1/mock-interviews", json={
            "user_id": "test_user_001",
            "skill": "Python",
            "difficulty_level": "intermediate"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Mock interview created successfully"
        assert "session_id" in data

    @pytest.mark.asyncio
    @patch("db_simple.create_mock_interview")
    async def test_create_mock_interview_failure(self, mock_create, client):
        mock_create.return_value = None
        
        response = await client.post("/api/v1/mock-interviews", json={
            "user_id": "test_user_001",
            "skill": "Python",
            "difficulty_level": "advanced"
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_mock_interview_missing_fields(self, client):
        response = await client.post("/api/v1/mock-interviews", json={
            "user_id": "test_user_001"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch("db_simple.get_user_mock_interviews")
    async def test_get_user_mock_interviews(self, mock_get, client):
        mock_get.return_value = [
            {
                "session_id": "mi_001",
                "user_id": "test_user_001",
                "skill": "Python",
                "difficulty_level": "intermediate",
                "status": "completed",
                "overall_score": 85
            }
        ]
        
        response = await client.get("/api/v1/users/test_user_001/mock-interviews")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["interviews"][0]["skill"] == "Python"

    @pytest.mark.asyncio
    @patch("db_simple.get_user_mock_interviews")
    async def test_get_mock_interviews_empty(self, mock_get, client):
        mock_get.return_value = []
        
        response = await client.get("/api/v1/users/new_user/mock-interviews")
        assert response.status_code == 200
        assert response.json()["count"] == 0


# ─── Dashboard Tests ──────────────────────────────────────────────────────────

class TestDashboard:
    """Test dashboard endpoints."""

    @pytest.mark.asyncio
    @patch("db_simple.get_user_dashboard")
    async def test_get_dashboard_success(self, mock_get, client, sample_user):
        mock_get.return_value = {
            "user_id": "test_user_001",
            "applications_count": 5,
            "total_interviews": 2,
            "profile_completion": 75,
            "stats": [],
            "recent_activity": []
        }
        
        response = await client.get("/api/v1/users/test_user_001/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user_001"
        assert data["applications_count"] == 5

    @pytest.mark.asyncio
    @patch("db_simple.get_user_dashboard")
    async def test_get_dashboard_not_found(self, mock_get, client):
        mock_get.return_value = None
        
        response = await client.get("/api/v1/users/nonexistent/dashboard")
        assert response.status_code == 404


# ─── Learning Resources Tests ─────────────────────────────────────────────────

class TestLearningResources:
    """Test learning resources endpoints."""

    @pytest.mark.asyncio
    @patch("db_simple.get_learning_resources")
    async def test_get_resources_no_filter(self, mock_get, client):
        mock_get.return_value = [
            {"title": "Python Basics", "skill": "Python", "level": "beginner"},
            {"title": "React Guide", "skill": "React", "level": "intermediate"}
        ]
        
        response = await client.get("/api/v1/learning-resources")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

    @pytest.mark.asyncio
    @patch("db_simple.get_learning_resources")
    async def test_get_resources_with_skill_filter(self, mock_get, client):
        mock_get.return_value = [
            {"title": "Python Basics", "skill": "Python", "level": "beginner"}
        ]
        
        response = await client.get("/api/v1/learning-resources?skill=Python")
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["skill"] == "Python"

    @pytest.mark.asyncio
    @patch("db_simple.get_learning_resources")
    async def test_get_resources_with_level_filter(self, mock_get, client):
        mock_get.return_value = []
        
        response = await client.get("/api/v1/learning-resources?level=advanced")
        assert response.status_code == 200
        assert response.json()["filters"]["level"] == "advanced"


# ─── User Progress Tests ──────────────────────────────────────────────────────

class TestUserProgress:
    """Test user progress endpoints."""

    @pytest.mark.asyncio
    @patch("db_simple.get_user_progress")
    async def test_get_progress_success(self, mock_get, client):
        mock_get.return_value = {
            "user_id": "test_user_001",
            "completed_resources": ["res_001"],
            "skill_levels": {"Python": "intermediate"},
            "total_learning_hours": 25
        }
        
        response = await client.get("/api/v1/users/test_user_001/progress")
        assert response.status_code == 200
        data = response.json()
        assert data["total_learning_hours"] == 25

    @pytest.mark.asyncio
    @patch("db_simple.get_user_progress")
    async def test_get_progress_not_found(self, mock_get, client):
        mock_get.return_value = None
        
        response = await client.get("/api/v1/users/nonexistent/progress")
        assert response.status_code == 404


# ─── Analytics Tests ──────────────────────────────────────────────────────────

class TestAnalytics:
    """Test analytics endpoint."""

    @pytest.mark.asyncio
    async def test_get_analytics_summary(self, client):
        response = await client.get("/api/v1/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_jobs" in data
