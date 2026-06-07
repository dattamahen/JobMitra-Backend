"""
E2E Tests for AI Content Generation endpoints.
Requires a running backend server at localhost:8000.
"""
import pytest
import httpx

BASE_URL = "http://localhost:8000"


@pytest.fixture
def api_url():
    return f"{BASE_URL}/api/v1"


class TestAIContentGenerationE2E:
    """E2E tests for /api/v1/profile/generate-ai-content."""

    @pytest.mark.asyncio
    async def test_generate_professional_summary_e2e(self, api_url):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{api_url}/profile/generate-ai-content", json={
                "type": "professional_summary",
                "current_role": "Senior Software Engineer",
                "current_company": "Amazon",
                "experience_years": 6,
                "skills": ["Python", "AWS", "FastAPI", "React", "PostgreSQL"],
                "highest_qualification": "masters",
                "desired_job_title": "Staff Engineer",
                "work_experience": [
                    {"company": "Amazon", "position": "SDE II", "description": "Built distributed systems"},
                    {"company": "Startup", "position": "Backend Dev", "description": "Led API development"}
                ]
            }, timeout=30.0)

            assert response.status_code == 200
            data = response.json()
            assert "content" in data
            assert len(data["content"]) > 50  # Should be a substantial summary

    @pytest.mark.asyncio
    async def test_generate_job_description_e2e(self, api_url):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{api_url}/profile/generate-ai-content", json={
                "type": "job_description",
                "position": "Senior Frontend Engineer",
                "company": "Google",
                "skills": ["React", "TypeScript", "GraphQL", "Next.js"],
                "experience_years": 5,
                "is_current": False
            }, timeout=30.0)

            assert response.status_code == 200
            data = response.json()
            assert "content" in data
            assert "•" in data["content"] or len(data["content"]) > 50

    @pytest.mark.asyncio
    async def test_invalid_type_returns_422(self, api_url):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{api_url}/profile/generate-ai-content", json={
                "type": "invalid",
                "skills": ["Python"]
            }, timeout=10.0)

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_type_returns_422(self, api_url):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{api_url}/profile/generate-ai-content", json={
                "current_role": "Developer"
            }, timeout=10.0)

            assert response.status_code == 422
