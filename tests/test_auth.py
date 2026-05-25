"""
Tests for Authentication endpoints.
Covers: register, login, logout, profile, change-password, forgot/reset password.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from datetime import datetime


@pytest.fixture
def app():
    """Create test app instance."""
    with patch("db_simple.db") as mock_db:
        mock_db.fallback_mode = False
        mock_db.database = MagicMock()
        mock_db.connect_to_mongo = AsyncMock()
        mock_db.close_mongo_connection = AsyncMock()
        
        from app import create_app
        return create_app()


@pytest.fixture
async def client(app):
    """Async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─── Registration Tests ───────────────────────────────────────────────────────

class TestRegistration:
    """Test user registration endpoint."""

    @pytest.mark.asyncio
    @patch("auth_db.create_user")
    async def test_register_success(self, mock_create, client, sample_user):
        mock_create.return_value = sample_user
        
        response = await client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
            "user_type": "candidate"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user["email"]
        assert data["first_name"] == sample_user["first_name"]

    @pytest.mark.asyncio
    async def test_register_missing_email(self, client):
        response = await client.post("/api/v1/auth/register", json={
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "short",
            "first_name": "New",
            "last_name": "User"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch("auth_db.create_user")
    async def test_register_duplicate_email(self, mock_create, client):
        mock_create.side_effect = ValueError("Email already registered")
        
        response = await client.post("/api/v1/auth/register", json={
            "email": "existing@example.com",
            "password": "SecurePass123!",
            "first_name": "Dup",
            "last_name": "User"
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_register_invalid_email_format(self, client):
        response = await client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "SecurePass123!",
            "first_name": "Bad",
            "last_name": "Email"
        })
        assert response.status_code == 422


# ─── Login Tests ──────────────────────────────────────────────────────────────

class TestLogin:
    """Test user login endpoint."""

    @pytest.mark.asyncio
    @patch("auth_db.authenticate_user")
    async def test_login_success(self, mock_auth, client, sample_user):
        mock_auth.return_value = sample_user
        
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "ValidPassword123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == sample_user["email"]

    @pytest.mark.asyncio
    @patch("auth_db.authenticate_user")
    async def test_login_invalid_credentials(self, mock_auth, client):
        mock_auth.return_value = None
        
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client):
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com"
        })
        assert response.status_code == 422


# ─── Protected Endpoint Tests ─────────────────────────────────────────────────

class TestProtectedEndpoints:
    """Test endpoints requiring authentication."""

    @pytest.mark.asyncio
    async def test_get_me_without_token(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_me_with_invalid_token(self, client):
        response = await client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid_token_here"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_id")
    async def test_get_me_with_valid_token(self, mock_get_user, client, sample_user, auth_headers):
        mock_get_user.return_value = sample_user
        
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == sample_user["user_id"]
        assert data["email"] == sample_user["email"]

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_id")
    async def test_logout_success(self, mock_get_user, client, sample_user, auth_headers):
        mock_get_user.return_value = sample_user
        
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"


# ─── Profile Update Tests ─────────────────────────────────────────────────────

class TestProfileUpdate:
    """Test profile update endpoint."""

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_id")
    @patch("auth_db.update_user_profile")
    @patch("activity_tracker.log_user_activity")
    async def test_update_profile_success(self, mock_log, mock_update, mock_get_user, client, sample_user, auth_headers):
        mock_get_user.return_value = sample_user
        mock_update.return_value = True
        mock_log.return_value = None
        
        response = await client.put("/api/v1/auth/profile", headers=auth_headers, json={
            "first_name": "Updated",
            "skills": ["Python", "React", "Docker"]
        })
        assert response.status_code == 200
        mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_profile_without_auth(self, client):
        response = await client.put("/api/v1/auth/profile", json={
            "first_name": "Hacker"
        })
        assert response.status_code in [401, 403]


# ─── Password Change Tests ────────────────────────────────────────────────────

class TestPasswordChange:
    """Test password change endpoint."""

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_id")
    @patch("auth_db.authenticate_user")
    @patch("auth_db.change_user_password")
    async def test_change_password_success(self, mock_change, mock_auth, mock_get_user, client, sample_user, auth_headers):
        mock_get_user.return_value = sample_user
        mock_auth.return_value = sample_user
        mock_change.return_value = True
        
        response = await client.post("/api/v1/auth/change-password", headers=auth_headers, json={
            "current_password": "OldPassword123!",
            "new_password": "NewPassword456!"
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_id")
    @patch("auth_db.authenticate_user")
    async def test_change_password_wrong_current(self, mock_auth, mock_get_user, client, sample_user, auth_headers):
        mock_get_user.return_value = sample_user
        mock_auth.return_value = None
        
        response = await client.post("/api/v1/auth/change-password", headers=auth_headers, json={
            "current_password": "WrongPassword",
            "new_password": "NewPassword456!"
        })
        assert response.status_code == 400


# ─── Forgot/Reset Password Tests ─────────────────────────────────────────────

class TestForgotResetPassword:
    """Test forgot and reset password flow."""

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_email")
    @patch("db_simple.db")
    @patch("email_service.email_service")
    async def test_forgot_password_existing_email(self, mock_email, mock_db, mock_get_user, client, sample_user):
        mock_get_user.return_value = sample_user
        mock_db.database = MagicMock()
        mock_db.database.__getitem__ = MagicMock(return_value=MagicMock(update_one=AsyncMock()))
        mock_email.send_password_reset_email.return_value = True
        
        response = await client.post("/api/v1/auth/forgot-password", json={
            "email": "test@example.com"
        })
        assert response.status_code == 200
        assert "reset link will be sent" in response.json()["message"]

    @pytest.mark.asyncio
    @patch("auth_db.get_user_by_email")
    async def test_forgot_password_nonexistent_email(self, mock_get_user, client):
        mock_get_user.return_value = None
        
        response = await client.post("/api/v1/auth/forgot-password", json={
            "email": "nonexistent@example.com"
        })
        # Should still return 200 to not leak user existence
        assert response.status_code == 200
