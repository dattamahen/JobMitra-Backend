"""
Tests for User Management endpoints.
Covers: create user, get user, update user profile.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport


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


class TestCreateUser:
    """Test user creation via /api/v1/users."""

    @pytest.mark.asyncio
    @patch("db_simple.create_user_profile")
    async def test_create_user_success(self, mock_create, client):
        mock_create.return_value = "inserted_id_123"
        
        response = await client.post("/api/v1/users", json={
            "user_id": "new_user_001",
            "email": "newuser@example.com",
            "full_name": "New User",
            "phone": "+1234567890",
            "skills": ["Python", "JavaScript"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user_id"] == "inserted_id_123"

    @pytest.mark.asyncio
    @patch("db_simple.create_user_profile")
    async def test_create_user_failure(self, mock_create, client):
        mock_create.return_value = None
        
        response = await client.post("/api/v1/users", json={
            "user_id": "fail_user",
            "email": "fail@example.com",
            "full_name": "Fail User"
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_user_missing_required_fields(self, client):
        response = await client.post("/api/v1/users", json={
            "full_name": "No Email User"
        })
        assert response.status_code == 422


class TestGetUser:
    """Test get user profile via /api/v1/users/{user_id}."""

    @pytest.mark.asyncio
    @patch("db_simple.get_user_profile")
    async def test_get_user_success(self, mock_get, client, sample_user):
        mock_get.return_value = sample_user
        
        response = await client.get("/api/v1/users/test_user_001")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user_001"
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    @patch("db_simple.get_user_profile")
    async def test_get_user_not_found(self, mock_get, client):
        mock_get.return_value = None
        
        response = await client.get("/api/v1/users/nonexistent_user")
        assert response.status_code == 404


class TestUpdateUser:
    """Test update user profile via /api/v1/users/{user_id}."""

    @pytest.mark.asyncio
    @patch("db_simple.update_user_profile")
    @patch("activity_tracker.log_user_activity")
    async def test_update_user_success(self, mock_log, mock_update, client):
        mock_update.return_value = True
        mock_log.return_value = None
        
        response = await client.put("/api/v1/users/test_user_001", json={
            "first_name": "Updated",
            "skills": [{"name": "Python", "level": "expert"}]
        })
        assert response.status_code == 200
        assert response.json()["message"] == "User updated successfully"

    @pytest.mark.asyncio
    @patch("db_simple.update_user_profile")
    async def test_update_user_not_found(self, mock_update, client):
        mock_update.return_value = False
        
        response = await client.put("/api/v1/users/nonexistent", json={
            "first_name": "Ghost"
        })
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_empty_body(self, client):
        response = await client.put("/api/v1/users/test_user_001", json={})
        assert response.status_code == 400
