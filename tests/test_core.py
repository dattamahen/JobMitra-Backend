"""
Tests for Core endpoints: health check, AI query, resume enhancement, logs.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def app():
    with patch("db.db") as mock_db:
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


# ─── Health Check Tests ───────────────────────────────────────────────────────

class TestHealthCheck:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_root_health_check(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_extended_health_check(self, client):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "features" in data
        assert "user_management" in data["features"]

    @pytest.mark.asyncio
    async def test_cors_test_endpoint(self, client):
        response = await client.get("/cors-test")
        assert response.status_code == 200
        assert "CORS is working" in response.json()["message"]


# ─── AI Query Tests ───────────────────────────────────────────────────────────

class TestAIQuery:
    """Test /ask endpoint."""

    @pytest.mark.asyncio
    @patch("crew_agent.run_crew_ai")
    @patch("db.log_to_db")
    async def test_ask_success(self, mock_log, mock_ai, client):
        mock_ai.return_value = {"answer": "FastAPI is a modern Python web framework."}
        mock_log.return_value = True
        
        response = await client.post("/ask", json={
            "query": "What is FastAPI?"
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_ask_empty_query(self, client):
        response = await client.post("/ask", json={
            "query": ""
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_ask_missing_query(self, client):
        response = await client.post("/ask", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch("crew_agent.run_crew_ai")
    async def test_ask_ai_failure(self, mock_ai, client):
        mock_ai.return_value = None
        
        response = await client.post("/ask", json={
            "query": "Test query"
        })
        assert response.status_code == 500


# ─── Resume Enhancement Tests ─────────────────────────────────────────────────

class TestResumeEnhancement:
    """Test /resume-enhance endpoint."""

    @pytest.mark.asyncio
    @patch("crew_agent.run_resume_enhancement_crew")
    @patch("db.log_to_db")
    async def test_enhance_resume_success(self, mock_log, mock_enhance, client):
        mock_enhance.return_value = {"enhanced_resume": "Enhanced version of the resume..."}
        mock_log.return_value = True
        
        response = await client.post("/resume-enhance", json={
            "resume": "John Doe, Python Developer with 5 years experience",
            "job_description": "Looking for a senior Python developer with FastAPI experience"
        })
        assert response.status_code == 200
        data = response.json()
        assert "enhanced_resume" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_enhance_resume_empty_resume(self, client):
        response = await client.post("/resume-enhance", json={
            "resume": "",
            "job_description": "Some job description"
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_enhance_resume_empty_job_description(self, client):
        response = await client.post("/resume-enhance", json={
            "resume": "Some resume content",
            "job_description": ""
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    @patch("crew_agent.run_resume_enhancement_crew")
    async def test_enhance_resume_ai_failure(self, mock_enhance, client):
        mock_enhance.return_value = None
        
        response = await client.post("/resume-enhance", json={
            "resume": "Resume content",
            "job_description": "Job description"
        })
        assert response.status_code == 500


# ─── Logs Tests ───────────────────────────────────────────────────────────────

class TestLogs:
    """Test logs endpoints."""

    @pytest.mark.asyncio
    @patch("db.get_query_logs")
    async def test_get_logs_success(self, mock_logs, client):
        mock_logs.return_value = [
            {"query": "test query", "response": "test response", "timestamp": "2024-01-01"}
        ]
        
        response = await client.get("/logs")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert data["count"] == 1

    @pytest.mark.asyncio
    @patch("db.get_query_logs")
    async def test_get_logs_with_limit(self, mock_logs, client):
        mock_logs.return_value = []
        
        response = await client.get("/logs?limit=5")
        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("db.get_query_logs")
    async def test_get_resume_logs(self, mock_logs, client):
        mock_logs.return_value = [
            {"query": "Resume Enhancement", "response": "enhanced", "metadata": {"process_type": "resume_enhancement"}}
        ]
        
        response = await client.get("/resume-logs")
        assert response.status_code == 200
        data = response.json()
        assert "resume_logs" in data
