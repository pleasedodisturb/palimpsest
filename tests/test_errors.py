"""Tests for structured error handling (CLI-05)."""

import io

import pytest

from palimpsest.errors import PalError, display_error


def test_pal_error_attributes():
    """CLI-05: PalError stores message and hint."""
    err = PalError("something broke", hint="try again")
    assert err.message == "something broke"
    assert err.hint == "try again"
    assert str(err) == "something broke"


def test_pal_error_no_hint():
    """CLI-05: PalError hint defaults to empty string."""
    err = PalError("something broke")
    assert err.hint == ""


def test_pal_error_is_exception():
    """PalError is a proper Exception subclass."""
    err = PalError("test")
    assert isinstance(err, Exception)


def test_display_error_renders_panel(capsys):
    """CLI-05: display_error writes styled error to stderr."""
    err = PalError("test error", hint="test hint")
    display_error(err, verbose=False)
    captured = capsys.readouterr()
    # Rich writes to stderr via err_console
    assert "test error" in captured.err
    assert "test hint" in captured.err


def test_display_error_without_hint(capsys):
    """CLI-05: display_error works without hint."""
    err = PalError("just an error")
    display_error(err, verbose=False)
    captured = capsys.readouterr()
    assert "just an error" in captured.err
