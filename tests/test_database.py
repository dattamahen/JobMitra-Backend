"""
Tests for database operations (db_simple.py).
Covers: CRUD operations, query logging, fallback mode.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from db_simple import (
    Database, log_to_db, get_query_logs,
    create_user_profile, get_user_profile, update_user_profile,
    search_jobs, create_job_application, get_user_applications,
    create_mock_interview, get_user_mock_interviews,
    get_user_dashboard, get_learning_resources, get_user_progress
)


class TestDatabaseConnection:
    """Test database connection and fallback mode."""

    def test_database_init_fallback_mode(self):
        with patch("db_simple.MONGODB_AVAILABLE", False):
            db = Database()
            assert db.fallback_mode is True

    @pytest.mark.asyncio
    async def test_connect_to_mongo_success(self):
        db = Database()
        with patch("db_simple.MONGODB_AVAILABLE", True):
            db.fallback_mode = False
            mock_client = MagicMock()
            mock_client.admin.command = AsyncMock(return_value=True)
            with patch("db_simple.AsyncIOMotorClient", return_value=mock_client):
                await db.connect_to_mongo()

    @pytest.mark.asyncio
    async def test_close_connection(self):
        db = Database()
        db.client = MagicMock()
        db.fallback_mode = False
        await db.close_mongo_connection()
        db.client.close.assert_called_once()


class TestQueryLogging:
    """Test query logging operations."""

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_log_to_db_success(self, mock_db):
        mock_collection = MagicMock()
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="log_id"))
        mock_db.fallback_mode = False
        mock_db.database = {"query_logs": mock_collection}
        
        result = await log_to_db("test query", "test response")
        assert result is True

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_log_to_db_fallback(self, mock_db):
        mock_db.fallback_mode = True
        mock_db.fallback_data = {"query_logs": []}
        
        result = await log_to_db("test query", "test response")
        assert result is True
        assert len(mock_db.fallback_data["query_logs"]) == 1

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_get_query_logs_success(self, mock_db):
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[
            {"_id": "id1", "query": "test", "response": "resp"}
        ])
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        mock_db.fallback_mode = False
        mock_db.database = {"query_logs": mock_collection}
        
        logs = await get_query_logs(limit=5)
        assert len(logs) == 1
        assert logs[0]["_id"] == "id1"


class TestUserOperations:
    """Test user CRUD operations."""

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_create_user_profile(self, mock_db):
        mock_collection = MagicMock()
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="user_id_123"))
        mock_db.fallback_mode = False
        mock_db.database = {"users": mock_collection}
        
        result = await create_user_profile({"user_id": "test", "email": "test@test.com"})
        assert result == "user_id_123"

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_get_user_profile_found(self, mock_db):
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value={
            "_id": "obj_id", "user_id": "test_001", "email": "test@test.com"
        })
        mock_db.fallback_mode = False
        mock_db.database = {"users": mock_collection}
        
        user = await get_user_profile("test_001")
        assert user is not None
        assert user["user_id"] == "test_001"

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_get_user_profile_not_found(self, mock_db):
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_db.fallback_mode = False
        mock_db.database = {"users": mock_collection}
        
        user = await get_user_profile("nonexistent")
        assert user is None

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_update_user_profile_success(self, mock_db):
        mock_collection = MagicMock()
        mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
        mock_db.fallback_mode = False
        mock_db.database = {"users": mock_collection}
        
        result = await update_user_profile("test_001", {"first_name": "Updated"})
        assert result is True

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_update_user_profile_not_found(self, mock_db):
        mock_collection = MagicMock()
        mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=0))
        mock_db.fallback_mode = False
        mock_db.database = {"users": mock_collection}
        
        result = await update_user_profile("nonexistent", {"first_name": "Ghost"})
        assert result is False


class TestJobOperations:
    """Test job search and application operations."""

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_search_jobs_with_query(self, mock_db):
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[
            {"_id": "id1", "job_id": "job_001", "title": "Python Dev"}
        ])
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        mock_db.fallback_mode = False
        mock_db.database = {"job_listings": mock_collection}
        
        jobs = await search_jobs(query="Python", limit=10)
        assert len(jobs) == 1

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_create_job_application(self, mock_db):
        mock_collection = MagicMock()
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="app_id"))
        mock_db.fallback_mode = False
        mock_db.database = {"job_applications": mock_collection}
        
        result = await create_job_application({"user_id": "u1", "job_id": "j1"})
        assert result == "app_id"


class TestMockInterviewOperations:
    """Test mock interview database operations."""

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_create_mock_interview(self, mock_db):
        mock_collection = MagicMock()
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="mi_id"))
        mock_db.fallback_mode = False
        mock_db.database = {"mock_interview_sessions": mock_collection}
        
        result = await create_mock_interview({"user_id": "u1", "skill": "Python"})
        assert result == "mi_id"

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_get_user_mock_interviews(self, mock_db):
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[
            {"_id": "id1", "session_id": "mi_001", "skill": "Python"}
        ])
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        mock_db.fallback_mode = False
        mock_db.database = {"mock_interview_sessions": mock_collection}
        
        interviews = await get_user_mock_interviews("test_user", limit=5)
        assert len(interviews) == 1


class TestLearningResources:
    """Test learning resources operations."""

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_get_resources_from_db(self, mock_db):
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[
            {"_id": "id1", "title": "Python Course", "skill": "Python"}
        ])
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        mock_db.fallback_mode = False
        mock_db.database = {"learning_resources": mock_collection}
        
        resources = await get_learning_resources(skill="Python")
        assert len(resources) == 1

    @pytest.mark.asyncio
    @patch("db_simple.db")
    async def test_get_resources_fallback_sample(self, mock_db):
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        mock_db.fallback_mode = False
        mock_db.database = {"learning_resources": mock_collection}
        
        resources = await get_learning_resources()
        # Should return sample data when DB is empty
        assert len(resources) >= 1
