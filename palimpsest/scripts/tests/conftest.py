"""Shared pytest fixtures for Palimpsest script tests."""

import importlib.util
import os
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def load_module():
    """Fixture that dynamically loads a Python module by file path.

    Usage in tests:
        def test_something(load_module):
            mod = load_module("content/upload_to_confluence.py")
            result = mod.markdown_to_confluence("# Hello")
    """
    def _load(relative_path):
        full_path = SCRIPTS_DIR / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"Module not found: {full_path}")

        module_name = full_path.stem
        spec = importlib.util.spec_from_file_location(module_name, str(full_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return _load


@pytest.fixture
def mock_env():
    """Fixture that patches environment variables for the duration of a test.

    Usage in tests:
        def test_with_env(mock_env):
            with mock_env(ATLASSIAN_DOMAIN="test.atlassian.net"):
                # env vars are set here
                pass
    """
    def _mock(**env_vars):
        return patch.dict(os.environ, env_vars, clear=False)

    return _mock
