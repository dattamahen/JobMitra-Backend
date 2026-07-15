"""
Tests for Job Management endpoints.
Covers: job search, job details, applications, resume tailor, apply.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from datetime import datetime


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


class TestJobSearch:
    """Test job search endpoint."""

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_id")
    @patch("db.db")
    async def test_search_jobs_success(self, mock_db, mock_get_user, client, sample_user, sample_job, auth_headers):
        mock_get_user.return_value = sample_user
        
        # Mock the database find operations
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[sample_job])
        mock_collection.find.return_value = mock_cursor
        mock_collection.find_one = AsyncMock(return_value=sample_user)
        
        mock_db.database = MagicMock()
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)
        
        response = await client.post("/api/v1/jobs/search", headers=auth_headers, json={
            "query": "python developer",
            "skills": ["Python"],
            "limit": 10
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_jobs_without_auth(self, client):
        response = await client.post("/api/v1/jobs/search", json={
            "query": "python"
        })
        assert response.status_code in [401, 403]


class TestJobDetails:
    """Test get job details endpoint."""

    @pytest.mark.asyncio
    async def test_get_job_details(self, client):
        response = await client.get("/api/v1/jobs/job_001")
        assert response.status_code == 200


class TestJobApplications:
    """Test job application endpoints."""

    @pytest.mark.asyncio
    @patch("db.create_job_application")
    async def test_create_application_success(self, mock_create, client):
        mock_create.return_value = "app_id_123"
        
        response = await client.post("/api/v1/applications", json={
            "user_id": "test_user_001",
            "job_id": "job_001",
            "cover_letter": "I am excited to apply..."
        })
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Application created successfully"

    @pytest.mark.asyncio
    @patch("db.create_job_application")
    async def test_create_application_failure(self, mock_create, client):
        mock_create.return_value = None
        
        response = await client.post("/api/v1/applications", json={
            "user_id": "test_user_001",
            "job_id": "job_001"
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_application_missing_fields(self, client):
        response = await client.post("/api/v1/applications", json={
            "cover_letter": "No user or job id"
        })
        assert response.status_code == 422


class TestResumeTailor:
    """Test resume tailor preview and apply endpoints."""

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_id")
    @patch("db.db")
    @patch("resume_tailor_agent.run_resume_tailor")
    async def test_tailor_preview_success(self, mock_tailor, mock_db, mock_get_user, client, sample_user, sample_job, auth_headers):
        mock_get_user.return_value = sample_user
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(side_effect=[sample_job, sample_user])
        mock_collection.update_one = AsyncMock()
        mock_db.database = MagicMock()
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)
        
        mock_tailor.return_value = {
            "tailored_resume": {
                "professional_summary": "Tailored summary",
                "skills": ["Python", "FastAPI"],
                "work_experience": [],
                "education": [],
                "projects": [],
                "certifications": []
            },
            "match_before": 60,
            "match_improvement": 85,
            "changes": [{"section": "summary", "type": "enhanced", "description": "Improved summary"}]
        }
        
        response = await client.get("/api/v1/jobs/job_001/tailor-preview", headers=auth_headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_tailor_preview_without_auth(self, client):
        response = await client.get("/api/v1/jobs/job_001/tailor-preview")
        assert response.status_code in [401, 403]


class TestCloseJob:
    """Test job close endpoint."""

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_id")
    @patch("db.db")
    async def test_close_job_success(self, mock_db, mock_get_user, client, sample_user, sample_job, auth_headers):
        mock_get_user.return_value = sample_user
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=sample_job)
        mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
        mock_db.database = MagicMock()
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)
        
        response = await client.patch("/api/v1/jobs/job_001/close", headers=auth_headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_id")
    @patch("db.db")
    async def test_close_job_not_found(self, mock_db, mock_get_user, client, sample_user, auth_headers):
        mock_get_user.return_value = sample_user
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_db.database = MagicMock()
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)
        
        response = await client.patch("/api/v1/jobs/nonexistent/close", headers=auth_headers)
        assert response.status_code == 404
