"""Tests for core/agent_marker.py — marker building and utility functions."""

import re
from unittest.mock import MagicMock, patch


def test_now_utc_format(load_module):
    mod = load_module("core/agent_marker.py")
    result = mod._now_utc()
    assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", result)


def test_actor_user_from_env(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    with mock_env(USER="testuser"):
        assert mod._actor_user() == "testuser"


def test_actor_user_fallback(load_module):
    mod = load_module("core/agent_marker.py")
    with patch.dict("os.environ", {}, clear=True):
        assert mod._actor_user() == "unknown"


def test_agent_name_default(load_module):
    mod = load_module("core/agent_marker.py")
    with patch.dict("os.environ", {}, clear=True):
        assert mod._agent_name() == "cursor"


def test_agent_name_custom(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    with mock_env(PAC_AGENT="claude-code"):
        assert mod._agent_name() == "claude-code"


def test_markers_enabled_default(load_module):
    mod = load_module("core/agent_marker.py")
    with patch.dict("os.environ", {}, clear=True):
        assert mod._markers_enabled() is True


def test_markers_disabled(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    with mock_env(ENABLE_AGENT_MARKERS="0"):
        assert mod._markers_enabled() is False


def test_markers_enabled_truthy_values(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    for val in ["1", "true", "True", "yes", "y", "YES"]:
        with mock_env(ENABLE_AGENT_MARKERS=val):
            assert mod._markers_enabled() is True, f"Expected True for '{val}'"


def test_build_marker_structure(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    with mock_env(PAC_AGENT="test-agent", USER="bob"):
        marker = mod.build_marker(action="upload", source="test.md")

    assert marker["action"] == "upload"
    assert marker["source"] == "test.md"
    assert marker["agent"] == "test-agent"
    assert marker["user"] == "bob"
    assert marker["marker_version"] == 1
    assert "uid" in marker
    assert "timestamp_utc" in marker
    assert len(marker["uid"]) == 32  # uuid4 hex


def test_build_marker_with_target_id(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    with mock_env(USER="alice"):
        marker = mod.build_marker(action="sync", source="s.md", target_id="abc123")
    assert marker["target_id"] == "abc123"


def test_build_marker_without_target_id(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    with mock_env(USER="alice"):
        marker = mod.build_marker(action="sync", source="s.md")
    assert "target_id" not in marker


def test_build_marker_with_extra(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    with mock_env(USER="alice"):
        marker = mod.build_marker(action="sync", source="s.md", extra={"page_version": 5})
    assert marker["page_version"] == 5


def test_upsert_drive_marker_disabled(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    mock_service = MagicMock()
    with mock_env(ENABLE_AGENT_MARKERS="0"):
        result = mod.upsert_drive_marker(mock_service, "file123", "upload", "test.md")
    assert result is False
    mock_service.files.assert_not_called()


def test_upsert_drive_marker_success(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    mock_service = MagicMock()
    mock_service.files().get().execute.return_value = {"appProperties": {}}
    mock_service.files().update().execute.return_value = {}

    with mock_env(ENABLE_AGENT_MARKERS="1", USER="bob", PAC_AGENT="test"):
        result = mod.upsert_drive_marker(mock_service, "file123", "upload", "test.md")
    assert result is True


def test_set_confluence_marker_dry_run(load_module):
    mod = load_module("core/agent_marker.py")
    result = mod.set_confluence_marker(
        page_id="123", headers={}, domain="test.atlassian.net",
        action="upload", source="test.md", dry_run=True,
    )
    assert result is True


def test_set_confluence_marker_disabled(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    with mock_env(ENABLE_AGENT_MARKERS="0"):
        result = mod.set_confluence_marker(
            page_id="123", headers={}, domain="test.atlassian.net",
            action="upload", source="test.md",
        )
    assert result is False
