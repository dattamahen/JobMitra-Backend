"""
Tests for default profile data feature.
Covers: random skill selection, random objective selection, integration with user creation.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


# ─── Unit Tests for default_profile_data module ──────────────────────────────

class TestDefaultProfileData:
    """Unit tests for default_profile_data.py functions."""

    def test_get_random_default_skills_returns_list(self):
        """TC-DP-001: get_random_default_skills returns a list."""
        from default_profile_data import get_random_default_skills
        skills = get_random_default_skills()
        assert isinstance(skills, list)

    def test_get_random_default_skills_returns_5_or_6(self):
        """TC-DP-002: Default call returns 5 or 6 skills."""
        from default_profile_data import get_random_default_skills
        for _ in range(20):
            skills = get_random_default_skills()
            assert len(skills) in [5, 6]

    def test_get_random_default_skills_custom_count(self):
        """TC-DP-003: Custom count returns exact number of skills."""
        from default_profile_data import get_random_default_skills
        assert len(get_random_default_skills(3)) == 3
        assert len(get_random_default_skills(10)) == 10

    def test_get_random_default_skills_no_duplicates(self):
        """TC-DP-004: Returned skills have no duplicates."""
        from default_profile_data import get_random_default_skills
        for _ in range(20):
            skills = get_random_default_skills()
            assert len(skills) == len(set(skills))

    def test_get_random_default_skills_from_valid_pool(self):
        """TC-DP-005: All returned skills exist in DEFAULT_SKILLS."""
        from default_profile_data import get_random_default_skills, DEFAULT_SKILLS
        for _ in range(20):
            skills = get_random_default_skills()
            for skill in skills:
                assert skill in DEFAULT_SKILLS

    def test_get_random_default_skills_randomness(self):
        """TC-DP-006: Multiple calls produce different results (probabilistic)."""
        from default_profile_data import get_random_default_skills
        results = [tuple(sorted(get_random_default_skills())) for _ in range(10)]
        # At least 2 unique combinations in 10 tries
        assert len(set(results)) >= 2

    def test_get_random_objective_returns_string(self):
        """TC-DP-007: get_random_objective returns a non-empty string."""
        from default_profile_data import get_random_objective
        obj = get_random_objective()
        assert isinstance(obj, str)
        assert len(obj) > 50

    def test_get_random_objective_from_valid_pool(self):
        """TC-DP-008: Returned objective exists in DEFAULT_OBJECTIVES."""
        from default_profile_data import get_random_objective, DEFAULT_OBJECTIVES
        for _ in range(20):
            obj = get_random_objective()
            assert obj in DEFAULT_OBJECTIVES

    def test_get_random_objective_randomness(self):
        """TC-DP-009: Multiple calls produce different objectives (probabilistic)."""
        from default_profile_data import get_random_objective
        results = [get_random_objective() for _ in range(20)]
        assert len(set(results)) >= 2

    def test_default_skills_pool_has_sufficient_entries(self):
        """TC-DP-010: DEFAULT_SKILLS has at least 90 entries."""
        from default_profile_data import DEFAULT_SKILLS
        assert len(DEFAULT_SKILLS) >= 90

    def test_default_objectives_pool_has_sufficient_entries(self):
        """TC-DP-011: DEFAULT_OBJECTIVES has at least 15 entries."""
        from default_profile_data import DEFAULT_OBJECTIVES
        assert len(DEFAULT_OBJECTIVES) >= 15

    def test_skills_are_non_empty_strings(self):
        """TC-DP-012: All skills in pool are non-empty strings."""
        from default_profile_data import DEFAULT_SKILLS
        for skill in DEFAULT_SKILLS:
            assert isinstance(skill, str)
            assert len(skill.strip()) > 0

    def test_objectives_are_non_empty_strings(self):
        """TC-DP-013: All objectives in pool are non-empty strings."""
        from default_profile_data import DEFAULT_OBJECTIVES
        for obj in DEFAULT_OBJECTIVES:
            assert isinstance(obj, str)
            assert len(obj.strip()) > 20


# ─── Integration Tests: create_user with defaults ────────────────────────────

class TestCreateUserWithDefaults:
    """Test that create_user assigns default skills and objective."""

    @pytest.mark.asyncio
    @patch("auth_db.db")
    async def test_create_user_assigns_default_skills_when_none_provided(self, mock_db):
        """TC-DP-014: User created without skills gets 5-6 random defaults."""
        from default_profile_data import DEFAULT_SKILLS

        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)

        from auth_db import create_user
        user = await create_user({
            "email": "newuser@test.com",
            "password": "TestPass123!",
            "first_name": "New",
            "last_name": "User",
            "user_type": "candidate"
        })

        assert "skills" in user
        assert len(user["skills"]) in [5, 6]
        for skill in user["skills"]:
            assert skill in DEFAULT_SKILLS

    @pytest.mark.asyncio
    @patch("auth_db.db")
    async def test_create_user_assigns_default_objective_when_none_provided(self, mock_db):
        """TC-DP-015: User created without summary gets a random objective."""
        from default_profile_data import DEFAULT_OBJECTIVES

        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)

        from auth_db import create_user
        user = await create_user({
            "email": "newuser2@test.com",
            "password": "TestPass123!",
            "first_name": "New",
            "last_name": "User",
            "user_type": "candidate"
        })

        assert "professional_summary" in user
        assert user["professional_summary"] in DEFAULT_OBJECTIVES

    @pytest.mark.asyncio
    @patch("auth_db.db")
    async def test_create_user_preserves_provided_skills(self, mock_db):
        """TC-DP-016: User created with explicit skills keeps them (no override)."""
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)

        from auth_db import create_user
        provided_skills = ["Python", "React", "Docker"]
        user = await create_user({
            "email": "skilled@test.com",
            "password": "TestPass123!",
            "first_name": "Skilled",
            "last_name": "Dev",
            "user_type": "candidate",
            "skills": provided_skills
        })

        assert user["skills"] == provided_skills

    @pytest.mark.asyncio
    @patch("auth_db.db")
    async def test_create_user_preserves_provided_summary(self, mock_db):
        """TC-DP-017: User created with explicit summary keeps it (no override)."""
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)

        from auth_db import create_user
        custom_summary = "I am a custom professional summary."
        user = await create_user({
            "email": "custom@test.com",
            "password": "TestPass123!",
            "first_name": "Custom",
            "last_name": "User",
            "user_type": "candidate",
            "professional_summary": custom_summary
        })

        assert user["professional_summary"] == custom_summary

    @pytest.mark.asyncio
    @patch("auth_db.db")
    async def test_create_user_syncs_skills_to_professional_info(self, mock_db):
        """TC-DP-018: Default skills are also set in professional_info.skills."""
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)

        from auth_db import create_user
        user = await create_user({
            "email": "sync@test.com",
            "password": "TestPass123!",
            "first_name": "Sync",
            "last_name": "User",
            "user_type": "candidate"
        })

        assert user["professional_info"]["skills"] == user["skills"]

    @pytest.mark.asyncio
    @patch("auth_db.db")
    async def test_create_user_syncs_summary_to_professional_info(self, mock_db):
        """TC-DP-019: Default objective is also set in professional_info.professional_summary."""
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)

        from auth_db import create_user
        user = await create_user({
            "email": "summary_sync@test.com",
            "password": "TestPass123!",
            "first_name": "Summary",
            "last_name": "Sync",
            "user_type": "candidate"
        })

        assert user["professional_info"]["professional_summary"] == user["professional_summary"]

    @pytest.mark.asyncio
    @patch("auth_db.db")
    async def test_create_user_empty_skills_list_gets_defaults(self, mock_db):
        """TC-DP-020: Empty skills list triggers default assignment."""
        from default_profile_data import DEFAULT_SKILLS

        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
        mock_db.database.__getitem__ = MagicMock(return_value=mock_collection)

        from auth_db import create_user
        user = await create_user({
            "email": "empty@test.com",
            "password": "TestPass123!",
            "first_name": "Empty",
            "last_name": "Skills",
            "user_type": "candidate",
            "skills": []
        })

        assert len(user["skills"]) in [5, 6]
        for skill in user["skills"]:
            assert skill in DEFAULT_SKILLS
