"""Shared fixtures for palimpsest test suite."""

import pytest
from typer.testing import CliRunner

from palimpsest.cli.main import app


@pytest.fixture
def runner():
    """Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def cli_app():
    """The main Typer app instance."""
    return app
