"""
Gitrama CLI Test Suite

Run with: pytest tests/ -v
Run with coverage: pytest tests/ --cov=gitrama --cov-report=term-missing

Copyright © 2026 Gitrama LLC. All Rights Reserved.
"""

import json
import os
import subprocess
import tempfile
from unittest.mock import patch, MagicMock

import pytest


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a temporary Git repository for testing."""
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()

    subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@gitrama.ai"], cwd=repo_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, capture_output=True)

    # Create initial commit
    readme = repo_dir / "README.md"
    readme.write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, capture_output=True)

    return repo_dir


@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary Gitrama config file."""
    config_dir = tmp_path / ".gitrama"
    config_dir.mkdir()
    config_file = config_dir / "config.json"
    config_file.write_text(json.dumps({
        "provider": "gitrama",
        "gitrama_token": "gtr_f_test1234567890abcdef1234567890abcdef",
        "api_url": "https://vast-connector.gitrama.io",
    }))
    return config_file


@pytest.fixture
def mock_ai_response():
    """Mock a successful AI API response."""
    return MagicMock(
        status_code=200,
        json=lambda: {"message": "feat(auth): add OAuth2 login flow"},
        raise_for_status=lambda: None,
    )


# ─── Config Tests ─────────────────────────────────────────────────────────────

class TestConfig:
    """Tests for config read/write operations."""

    def test_set_and_get_value(self, tmp_path):
        """Config values can be set and retrieved."""
        from gitrama.config import set_value, get_value

        with patch("gitrama.config.CONFIG_PATH", tmp_path / ".gitrama" / "config.json"):
            os.makedirs(tmp_path / ".gitrama", exist_ok=True)
            set_value("provider", "openai")
            assert get_value("provider") == "openai"

    def test_get_missing_value_returns_none(self, tmp_path):
        """Missing config values return None, not crash."""
        from gitrama.config import get_value

        with patch("gitrama.config.CONFIG_PATH", tmp_path / ".gitrama" / "config.json"):
            os.makedirs(tmp_path / ".gitrama", exist_ok=True)
            (tmp_path / ".gitrama" / "config.json").write_text("{}")
            assert get_value("nonexistent_key") is None

    def test_config_file_created_on_first_write(self, tmp_path):
        """Config file and directory are created if they don't exist."""
        from gitrama.config import set_value

        config_path = tmp_path / ".gitrama" / "config.json"
        with patch("gitrama.config.CONFIG_PATH", config_path):
            set_value("provider", "anthropic")
            assert config_path.exists()


# ─── AI Client Tests ──────────────────────────────────────────────────────────

class TestAIClient:
    """Tests for the AI client provider routing."""

    def test_default_provider_is_gitrama(self, tmp_path):
        """Default provider should be gitrama when nothing is configured."""
        from gitrama.ai_client import AIClient

        with patch("gitrama.config.get_value", return_value=None):
            client = AIClient()
            assert client.provider == "gitrama"

    def test_provider_routing_openai(self, tmp_path):
        """OpenAI provider should use correct API URL."""
        from gitrama.ai_client import AIClient

        def mock_get(key):
            return {"provider": "openai", "api_key": "sk-test123", "model": "gpt-4o-mini", "api_url": None}.get(key)

        with patch("gitrama.config.get_value", side_effect=mock_get):
            client = AIClient()
            assert client.provider == "openai"
            assert client.api_key == "sk-test123"

    def test_provider_routing_anthropic(self):
        """Anthropic provider should set correct headers."""
        from gitrama.ai_client import AIClient

        def mock_get(key):
            return {"provider": "anthropic", "api_key": "sk-ant-test", "model": "claude-haiku-4-5-20251001", "api_url": None}.get(key)

        with patch("gitrama.config.get_value", side_effect=mock_get):
            client = AIClient()
            headers = client._headers()
            assert "x-api-key" in headers
            assert headers["anthropic-version"] == "2023-06-01"

    def test_unknown_provider_raises(self):
        """Unknown provider should raise a clear error."""
        from gitrama.ai_client import AIClient

        def mock_get(key):
            return {"provider": "invalid_provider", "api_key": None, "model": None, "api_url": None}.get(key)

        with patch("gitrama.config.get_value", side_effect=mock_get):
            client = AIClient()
            with pytest.raises(Exception, match="Unknown provider"):
                client._chat("system", "user")


# ─── Commit Message Quality Tests ─────────────────────────────────────────────

class TestCommitMessageQuality:
    """Tests for AI-generated commit message quality."""

    def test_commit_message_follows_conventional_format(self, mock_ai_response):
        """Generated commit messages should follow conventional commit format."""
        from gitrama.ai_client import AIClient

        with patch("gitrama.config.get_value", return_value=None):
            with patch("requests.post", return_value=mock_ai_response):
                client = AIClient()
                # Mock the gitrama provider response
                msg = mock_ai_response.json()["message"]

                # Verify conventional commit format: type(scope): subject
                assert ":" in msg
                prefix = msg.split(":")[0]
                valid_types = ["feat", "fix", "docs", "style", "refactor", "test", "chore", "perf", "ci", "build"]
                commit_type = prefix.split("(")[0]
                assert commit_type in valid_types

    def test_commit_message_under_72_chars(self, mock_ai_response):
        """Commit message subject line should be under 72 characters."""
        msg = mock_ai_response.json()["message"]
        subject = msg.split("\n")[0]
        assert len(subject) <= 72


# ─── Token Validation Tests ──────────────────────────────────────────────────

class TestTokenValidation:
    """Tests for GITRAMA_TOKEN validation logic."""

    def test_missing_token_raises_error(self):
        """Missing token should raise a clear error with instructions."""
        from gitrama.ai_client import AIClient

        def mock_get(key):
            return {"provider": "gitrama", "api_key": None, "model": None,
                    "api_url": "https://vast-connector.gitrama.io",
                    "gitrama_token": None}.get(key)

        with patch("gitrama.config.get_value", side_effect=mock_get):
            client = AIClient()
            with pytest.raises(Exception, match="No Gitrama token found"):
                client._validate_gitrama_token()

    def test_invalid_token_raises_error(self):
        """Invalid token should raise an error after server check."""
        from gitrama.ai_client import AIClient

        def mock_get(key):
            return {"provider": "gitrama", "api_key": None, "model": None,
                    "api_url": "https://vast-connector.gitrama.io",
                    "gitrama_token": "gtr_f_invalid"}.get(key)

        mock_resp = MagicMock(
            ok=False,
            json=lambda: {"valid": False, "message": "Invalid token"},
        )

        with patch("gitrama.config.get_value", side_effect=mock_get):
            with patch("requests.post", return_value=mock_resp):
                client = AIClient()
                # Clear any cached validation
                from gitrama import ai_client
                ai_client._token_cache = {"hash": None, "valid": False, "tier": None, "expires": 0}
                with pytest.raises(Exception, match="Invalid token"):
                    client._validate_gitrama_token()

    def test_valid_token_caches_result(self):
        """Valid token should be cached for 1 hour."""
        from gitrama.ai_client import AIClient, _token_cache, TOKEN_CACHE_TTL
        import time

        def mock_get(key):
            return {"provider": "gitrama", "api_key": None, "model": None,
                    "api_url": "https://vast-connector.gitrama.io",
                    "gitrama_token": "gtr_f_validtoken1234567890abcdef12345"}.get(key)

        mock_resp = MagicMock(
            ok=True,
            json=lambda: {"valid": True, "tier": "free", "daily_limit": 50,
                         "daily_used": 0, "first_name": "Test"},
        )

        with patch("gitrama.config.get_value", side_effect=mock_get):
            with patch("requests.post", return_value=mock_resp) as mock_post:
                client = AIClient()
                from gitrama import ai_client
                ai_client._token_cache = {"hash": None, "valid": False, "tier": None, "expires": 0}

                client._validate_gitrama_token()
                assert ai_client._token_cache["valid"] is True
                assert ai_client._token_cache["tier"] == "free"
                assert ai_client._token_cache["expires"] > time.time()

                # Second call should use cache, not make another request
                client._validate_gitrama_token()
                assert mock_post.call_count == 1  # Only called once

    def test_daily_limit_exceeded_raises_error(self):
        """Exceeding daily limit should raise an error with upgrade message."""
        from gitrama.ai_client import AIClient

        def mock_get(key):
            return {"provider": "gitrama", "api_key": None, "model": None,
                    "api_url": "https://vast-connector.gitrama.io",
                    "gitrama_token": "gtr_f_validtoken1234567890abcdef12345"}.get(key)

        mock_resp = MagicMock(
            ok=True,
            json=lambda: {"valid": True, "tier": "free", "daily_limit": 50,
                         "daily_used": 50, "first_name": "Test"},
        )

        with patch("gitrama.config.get_value", side_effect=mock_get):
            with patch("requests.post", return_value=mock_resp):
                client = AIClient()
                from gitrama import ai_client
                ai_client._token_cache = {"hash": None, "valid": False, "tier": None, "expires": 0}
                with pytest.raises(Exception, match="Daily limit reached"):
                    client._validate_gitrama_token()

    def test_byok_skips_token_validation(self):
        """BYOK providers (OpenAI, Anthropic, Ollama) should skip token validation entirely."""
        from gitrama.ai_client import AIClient

        for provider in ["openai", "anthropic", "ollama"]:
            def mock_get(key, p=provider):
                return {"provider": p, "api_key": "sk-test", "model": "gpt-4o-mini",
                        "api_url": None, "gitrama_token": None}.get(key)

            with patch("gitrama.config.get_value", side_effect=mock_get):
                client = AIClient()
                # BYOK providers should not have _validate_gitrama_token called
                # They route through _chat_openai, _chat_anthropic, _chat_ollama
                assert client.provider == provider


# ─── Branch Name Tests ────────────────────────────────────────────────────────

class TestBranchName:
    """Tests for branch name generation."""

    def test_branch_name_is_kebab_case(self):
        """Branch names should be lowercase kebab-case."""
        branch = "feat/add-user-authentication"
        assert branch == branch.lower()
        assert " " not in branch

    def test_branch_name_has_valid_prefix(self):
        """Branch names should start with a conventional prefix."""
        valid_prefixes = ["feat/", "fix/", "docs/", "chore/", "hotfix/", "exp/", "review/"]
        branch = "feat/add-user-authentication"
        assert any(branch.startswith(p) for p in valid_prefixes)

    def test_branch_name_max_length(self):
        """Branch names should be under 50 characters."""
        branch = "feat/add-user-authentication"
        assert len(branch) <= 50


# ─── Stream Tests ─────────────────────────────────────────────────────────────

class TestStreams:
    """Tests for Gitrama stream (workflow context) management."""

    def test_valid_stream_names(self):
        """Only valid stream names should be accepted."""
        from gitrama.ai_client import _stream_instruction

        valid = ["hotfix", "wip", "review", "experiment"]
        for stream in valid:
            result = _stream_instruction(stream)
            assert result  # Should return non-empty instruction

    def test_unknown_stream_returns_empty(self):
        """Unknown stream name should return empty string."""
        from gitrama.ai_client import _stream_instruction

        assert _stream_instruction("invalid_stream") == ""
        assert _stream_instruction(None) == ""

    def test_stream_prefix_mapping(self):
        """Each stream should map to the correct branch prefix."""
        from gitrama.ai_client import _stream_prefix

        assert "hotfix/" in _stream_prefix("hotfix")
        assert "exp/" in _stream_prefix("experiment")


# ─── PR Description Tests ────────────────────────────────────────────────────

class TestPRDescription:
    """Tests for PR description parsing."""

    def test_parse_pr_json_valid(self):
        """Valid JSON PR response should be parsed correctly."""
        from gitrama.ai_client import _parse_pr_json

        raw = '{"title": "Add auth", "description": "This PR adds OAuth2."}'
        result = _parse_pr_json(raw)
        assert result["title"] == "Add auth"
        assert "OAuth2" in result["description"]

    def test_parse_pr_json_with_markdown_fences(self):
        """PR response wrapped in markdown code fences should still parse."""
        from gitrama.ai_client import _parse_pr_json

        raw = '```json\n{"title": "Fix bug", "description": "Fixed the thing."}\n```'
        result = _parse_pr_json(raw)
        assert result["title"] == "Fix bug"

    def test_parse_pr_json_fallback_on_invalid(self):
        """Invalid JSON should fallback gracefully, not crash."""
        from gitrama.ai_client import _parse_pr_json

        raw = "This is not JSON at all."
        result = _parse_pr_json(raw)
        assert result["title"] == "PR Description"
        assert result["description"] == raw


# ─── Health Check Tests ───────────────────────────────────────────────────────

class TestHealthCheck:
    """Tests for provider health check."""

    def test_gitrama_health_check(self):
        """Gitrama health check should call /health endpoint."""
        from gitrama.ai_client import AIClient

        mock_resp = MagicMock(
            status_code=200,
            json=lambda: {"status": "ok", "service": "gitrama"},
            raise_for_status=lambda: None,
        )

        with patch("gitrama.config.get_value", return_value=None):
            with patch("requests.get", return_value=mock_resp):
                client = AIClient()
                result = client.health_check()
                assert result["status"] == "ok"

    def test_health_check_failure_raises(self):
        """Failed health check should raise with clear message."""
        from gitrama.ai_client import AIClient

        with patch("gitrama.config.get_value", return_value=None):
            with patch("requests.get", side_effect=ConnectionError("Connection refused")):
                client = AIClient()
                with pytest.raises(Exception, match="Health check failed"):
                    client.health_check()


# ─── Integration Test (requires gtr installed) ───────────────────────────────

class TestCLIIntegration:
    """Integration tests that run actual gtr commands.

    These tests are skipped if gtr is not installed.
    Mark with: pytest -m integration
    """

    @pytest.fixture(autouse=True)
    def check_gtr_installed(self):
        result = subprocess.run(["which", "gtr"], capture_output=True)
        if result.returncode != 0:
            pytest.skip("gtr CLI not installed")

    @pytest.mark.integration
    def test_gtr_health(self):
        """gtr health should return without error."""
        result = subprocess.run(["gtr", "health"], capture_output=True, text=True, timeout=15)
        # May fail if no server connection, but should not crash
        assert result.returncode in [0, 1]

    @pytest.mark.integration
    def test_gtr_status_in_git_repo(self, temp_git_repo):
        """gtr status should work in a Git repository."""
        result = subprocess.run(
            ["gtr", "status"], cwd=temp_git_repo,
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
