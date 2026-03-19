"""Entry point for pal / palimpsest CLI."""

from __future__ import annotations

import typer
from importlib.metadata import version as pkg_version, PackageNotFoundError

from palimpsest.console import console
from palimpsest.errors import PalError, display_error

app = typer.Typer(
    name="pal",
    help="AI-augmented Technical Program Management toolkit.",
    rich_markup_mode="rich",
    no_args_is_help=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

# Module-level state for verbose/quiet flags (read by subcommands)
_state: dict[str, bool] = {"verbose": False, "quiet": False}


def _version_callback(value: bool) -> None:
    """Print version and exit when --version is passed."""
    if value:
        try:
            ver = pkg_version("palimpsest")
        except PackageNotFoundError:
            ver = "0.0.0-dev"
        console.print(f"palimpsest [bold]{ver}[/bold]")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Minimal output.",
    ),
) -> None:
    """AI-augmented Technical Program Management toolkit."""
    _state["verbose"] = verbose
    _state["quiet"] = quiet


def run() -> None:
    """Entry point for console_scripts (pyproject.toml [project.scripts])."""
    try:
        app()
    except PalError as e:
        display_error(e, verbose=_state.get("verbose", False))
        raise typer.Exit(code=1) from None
