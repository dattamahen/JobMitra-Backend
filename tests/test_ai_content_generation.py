"""
Tests for AI Content Generation endpoints: professional summary and job description.
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


class TestGenerateProfessionalSummary:
    """Test POST /api/v1/profile/generate-ai-content with type=professional_summary."""

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_summary_success(self, mock_llm, client):
        mock_llm.return_value = {
            "content": "Experienced Python developer with 5+ years building scalable web applications using FastAPI and Django."
        }

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "professional_summary",
            "current_role": "Senior Python Developer",
            "current_company": "TechCorp",
            "experience_years": 5,
            "skills": ["Python", "FastAPI", "Django", "MongoDB"],
            "highest_qualification": "masters",
            "desired_job_title": "Lead Developer"
        })

        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert len(data["content"]) > 0

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_summary_with_work_experience(self, mock_llm, client):
        mock_llm.return_value = {
            "content": "Full-stack engineer with proven track record at top companies."
        }

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "professional_summary",
            "current_role": "Full Stack Developer",
            "experience_years": 3,
            "skills": ["React", "Node.js", "TypeScript"],
            "work_experience": [
                {"company": "Google", "position": "SDE II", "description": "Built microservices"},
                {"company": "Startup", "position": "Full Stack Dev", "description": "Led frontend team"}
            ]
        })

        assert response.status_code == 200
        assert "content" in response.json()

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_summary_with_projects_and_certs(self, mock_llm, client):
        mock_llm.return_value = {"content": "AWS certified cloud architect."}

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "professional_summary",
            "current_role": "Cloud Engineer",
            "experience_years": 7,
            "skills": ["AWS", "Terraform", "Kubernetes"],
            "projects": [{"name": "Cloud Migration", "technologies": "AWS, Terraform"}],
            "certifications": [{"name": "AWS Solutions Architect"}]
        })

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_summary_minimal_data(self, mock_llm, client):
        mock_llm.return_value = {"content": "Aspiring developer eager to learn."}

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "professional_summary",
            "experience_years": 0,
            "skills": ["Python"]
        })

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_summary_empty_response(self, mock_llm, client):
        mock_llm.return_value = {"content": ""}

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "professional_summary",
            "current_role": "Developer",
            "skills": ["Java"]
        })

        assert response.status_code == 500

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_summary_llm_exception(self, mock_llm, client):
        mock_llm.side_effect = Exception("LLM service unavailable")

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "professional_summary",
            "current_role": "Developer",
            "skills": ["Python"]
        })

        assert response.status_code == 500


class TestGenerateJobDescription:
    """Test POST /api/v1/profile/generate-ai-content with type=job_description."""

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_job_description_success(self, mock_llm, client):
        mock_llm.return_value = {
            "content": "• Architected microservices handling 10M+ requests/day\n• Reduced API latency by 40%"
        }

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "job_description",
            "position": "Senior Backend Engineer",
            "company": "Netflix",
            "skills": ["Python", "Go", "Kubernetes", "gRPC"],
            "experience_years": 6,
            "is_current": False
        })

        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert len(data["content"]) > 0

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_job_description_current_role(self, mock_llm, client):
        mock_llm.return_value = {
            "content": "• Leading a team of 8 engineers building real-time data pipelines"
        }

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "job_description",
            "position": "Engineering Manager",
            "company": "DataCorp",
            "skills": ["Python", "Spark", "Kafka"],
            "experience_years": 10,
            "is_current": True
        })

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_job_description_minimal(self, mock_llm, client):
        mock_llm.return_value = {"content": "• Developed web applications using React"}

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "job_description",
            "position": "Frontend Developer"
        })

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_job_description_empty_response(self, mock_llm, client):
        mock_llm.return_value = {"content": ""}

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "job_description",
            "position": "Developer"
        })

        assert response.status_code == 500

    @pytest.mark.asyncio
    @patch("professional_summary_endpoints.llm_service.generate")
    async def test_generate_job_description_llm_exception(self, mock_llm, client):
        mock_llm.side_effect = Exception("LLM timeout")

        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "job_description",
            "position": "Developer",
            "company": "Corp"
        })

        assert response.status_code == 500


class TestGenerateAIContentValidation:
    """Test input validation for the unified endpoint."""

    @pytest.mark.asyncio
    async def test_missing_type_field(self, client):
        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "current_role": "Developer"
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_type_field(self, client):
        response = await client.post("/api/v1/profile/generate-ai-content", json={
            "type": "invalid_type",
            "current_role": "Developer"
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_body(self, client):
        response = await client.post("/api/v1/profile/generate-ai-content", json={})

        assert response.status_code == 422
