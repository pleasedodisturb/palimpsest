"""TDD RED tests for Task 1: Console singleton, error handling, and CLI with global flags."""

from typer.testing import CliRunner


def test_version():
    """pal --version exits 0 and output contains 'palimpsest' and '0.1.0'."""
    from palimpsest.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "palimpsest" in result.output
    assert "0.1.0" in result.output


def test_help():
    """pal --help exits 0 and output contains 'Usage', '--version', '--verbose', '--quiet'."""
    from palimpsest.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "--version" in result.output
    assert "--verbose" in result.output
    assert "--quiet" in result.output


def test_no_args_shows_help():
    """pal with no args shows help text (no_args_is_help=True)."""
    from palimpsest.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, [])
    # Typer's no_args_is_help exits with code 0 or 2 depending on version;
    # the important behavior is that help text IS displayed
    assert "Usage" in result.output


def test_pal_error_panel(capsys):
    """PalError('msg', hint='fix') displays Rich panel with 'msg' and 'fix' text."""
    from palimpsest.errors import PalError, display_error

    err = PalError("msg", hint="fix")
    display_error(err, verbose=False)
    captured = capsys.readouterr()
    assert "msg" in captured.err
    assert "fix" in captured.err


def test_display_error_verbose(capsys):
    """display_error with verbose=True includes traceback output."""
    from palimpsest.errors import PalError, display_error

    try:
        raise PalError("verbose test", hint="check")
    except PalError as e:
        display_error(e, verbose=True)
    captured = capsys.readouterr()
    assert "verbose test" in captured.err
    assert "Traceback" in captured.err or "PalError" in captured.err


def test_console_has_pal_theme():
    """console object has PAL_THEME with keys: info, success, warning, error, hint, command."""
    from palimpsest.console import PAL_THEME

    for key in ["info", "success", "warning", "error", "hint", "command"]:
        assert key in PAL_THEME.styles, f"Missing theme key: {key}"


def test_err_console_writes_to_stderr():
    """err_console writes to stderr."""
    from palimpsest.console import err_console

    assert err_console.stderr is True
