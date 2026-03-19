"""Structured error handling with Rich panels for user-facing errors."""

import typer
from rich.panel import Panel

from palimpsest.console import err_console


class PalError(Exception):
    """User-facing error with message and optional fix suggestion."""

    def __init__(self, message: str, hint: str = "") -> None:
        self.message = message
        self.hint = hint
        super().__init__(message)


def display_error(error: PalError, verbose: bool = False) -> None:
    """Display a PalError as a Rich panel on stderr.

    Shows the error message and optional hint. In verbose mode,
    also prints the full Python traceback.
    """
    parts = [f"[error]{error.message}[/error]"]
    if error.hint:
        parts.append(f"\n[hint]Hint: {error.hint}[/hint]")
    err_console.print(
        Panel("\n".join(parts), title="[error]error[/error]", border_style="red")
    )
    if verbose:
        err_console.print_exception(show_locals=False)
