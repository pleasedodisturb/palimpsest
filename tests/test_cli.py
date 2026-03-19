"""Tests for the pal CLI entry point."""

from typer.testing import CliRunner
from palimpsest.cli.main import app

runner = CliRunner()


def test_version():
    """CLI-03: pal --version prints version string."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "palimpsest" in result.output


def test_version_short_flag():
    """CLI-03: pal -V also prints version."""
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert "palimpsest" in result.output


def test_help():
    """CLI-02: pal --help shows usage info."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_help_shows_global_flags():
    """CLI-02: Help text includes all global flags."""
    result = runner.invoke(app, ["--help"])
    assert "--version" in result.output
    assert "--verbose" in result.output
    assert "--quiet" in result.output


def test_no_args_shows_help():
    """CLI-02: Running pal with no arguments shows help."""
    result = runner.invoke(app, [])
    # Typer's no_args_is_help shows help text; exit code may be 0 or 2
    assert "Usage" in result.output


def test_verbose_flag_accepted():
    """CLI flag: --verbose does not cause error."""
    result = runner.invoke(app, ["--verbose", "--help"])
    assert result.exit_code == 0


def test_quiet_flag_accepted():
    """CLI flag: --quiet does not cause error."""
    result = runner.invoke(app, ["--quiet", "--help"])
    assert result.exit_code == 0


def test_version_contains_semver():
    """CLI-03: Version output contains a semver-like string."""
    result = runner.invoke(app, ["--version"])
    # Should contain something like "0.1.0" or "0.0.0-dev"
    output = result.output.strip()
    assert any(c.isdigit() for c in output), f"No version number in: {output}"
