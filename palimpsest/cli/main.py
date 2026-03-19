"""Entry point for pal / palimpsest CLI."""

import typer

app = typer.Typer(
    name="pal",
    help="AI-augmented Technical Program Management toolkit.",
    no_args_is_help=True,
)


@app.callback()
def callback() -> None:
    """AI-augmented Technical Program Management toolkit."""
    pass


def run() -> None:
    """Entry point for console_scripts."""
    app()
