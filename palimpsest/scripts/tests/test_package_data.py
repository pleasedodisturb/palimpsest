"""Integration tests for package data accessibility (PKG-01)."""

from importlib.resources import files
from pathlib import Path

import pytest


@pytest.fixture
def package_root():
    """Return the Traversable root of the palimpsest package."""
    return files("palimpsest")


class TestPackageStructure:
    """Verify all content directories are discoverable as package data."""

    CONTENT_DIRS = [
        "docs",
        "templates",
        "agents",
        "playbooks",
        "case-study",
        "showcase",
        "project-template",
        "example",
    ]

    def test_package_root_exists(self, package_root):
        assert package_root is not None

    @pytest.mark.parametrize("dirname", CONTENT_DIRS)
    def test_content_directory_exists(self, package_root, dirname):
        subdir = package_root.joinpath(dirname)
        assert subdir.is_dir(), f"{dirname}/ not found in package"

    def test_templates_contain_md_files(self, package_root):
        templates = package_root.joinpath("templates")
        md_files = [f.name for f in templates.iterdir() if f.name.endswith(".md")]
        assert len(md_files) > 0, "No .md files found in templates/"

    def test_agents_contain_config_files(self, package_root):
        agents = package_root.joinpath("agents")
        # Should have subdirectories for each agent
        subdirs = [f.name for f in agents.iterdir() if f.is_dir() and f.name != "__pycache__"]
        assert "claude-code" in subdirs
        assert "cursor" in subdirs

    def test_template_file_readable(self, package_root):
        """Verify a template file can be read as text."""
        templates = package_root.joinpath("templates")
        md_files = [f for f in templates.iterdir() if f.name.endswith((".md", ".template"))]
        assert len(md_files) > 0
        content = md_files[0].read_text()
        assert len(content) > 0


class TestPackageMetadata:
    """Verify package metadata and helper functions."""

    def test_version_exists(self):
        import palimpsest
        assert hasattr(palimpsest, "__version__")
        assert isinstance(palimpsest.__version__, str)
        assert len(palimpsest.__version__) > 0

    def test_data_read_template(self):
        from palimpsest.data import read_template
        # Get any template file name
        templates = files("palimpsest").joinpath("templates")
        md_files = [f.name for f in templates.iterdir() if f.name.endswith((".md", ".template"))]
        assert len(md_files) > 0
        content = read_template(md_files[0])
        assert len(content) > 0

    def test_data_read_doc(self):
        from palimpsest.data import read_doc
        docs = files("palimpsest").joinpath("docs")
        md_files = [f.name for f in docs.iterdir() if f.name.endswith(".md")]
        assert len(md_files) > 0
        content = read_doc(md_files[0])
        assert len(content) > 0
