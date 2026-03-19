"""Tests for content bundling and access (DIST-02)."""

from pathlib import Path

import pytest

from palimpsest.content import (
    CONTENT_CATEGORIES,
    get_content_path,
    list_content,
)


def test_content_categories_defined():
    """DIST-02: All expected content categories are defined."""
    expected = {"docs", "templates", "agents", "playbooks", "showcase", "case-study"}
    assert expected == set(CONTENT_CATEGORIES)


def test_list_content_docs():
    """DIST-02: docs category contains methodology guides."""
    docs = list_content("docs")
    assert "01-problem-statement.md" in docs
    assert "10-privacy-model.md" in docs
    assert len(docs) >= 10


def test_list_content_templates():
    """DIST-02: templates category contains TPM templates."""
    templates = list_content("templates")
    assert "prd.md" in templates
    assert "brd.md" in templates


def test_list_content_playbooks():
    """DIST-02: playbooks category contains playbooks."""
    playbooks = list_content("playbooks")
    assert "remote-onboarding.md" in playbooks
    assert len(playbooks) >= 4


def test_list_content_showcase():
    """DIST-02: showcase category contains demo content."""
    showcase = list_content("showcase")
    assert "quick-wins.md" in showcase


def test_list_content_case_study():
    """DIST-02: case-study category contains narrative."""
    case_study = list_content("case-study")
    assert "wolt-crm-migration.md" in case_study


def test_list_content_agents():
    """DIST-02: agents category contains agent configs."""
    agents = list_content("agents")
    assert "README.md" in agents


def test_list_content_invalid_category():
    """Error handling: invalid category raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Unknown content category"):
        list_content("nonexistent")


def test_get_content_path_valid():
    """DIST-02: get_content_path returns existing Path for valid file."""
    path = get_content_path("docs", "01-problem-statement.md")
    assert isinstance(path, Path)
    assert path.exists()
    assert path.name == "01-problem-statement.md"


def test_get_content_path_invalid_file():
    """Error handling: nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Content file not found"):
        get_content_path("docs", "nonexistent.md")


def test_get_content_path_invalid_category():
    """Error handling: invalid category raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Unknown content category"):
        get_content_path("nonexistent", "file.md")
